"""Leakage tests 3 and 4 using the reported run's saved predictions.
3. Cut-offs must not depend on test labels: randomise all test labels, recompute scores/cut-offs exactly as notebook 04 -> identical.
4. Placebo: shift each building's labeled events by a random number of hours inside the test period; recall must collapse to chance."""
import pandas as pd,numpy as np,json
O='/home/claude/rerun/ProjectFull/outputs_full/'
T0=pd.Timestamp('2016-01-01');TRAIN_END=pd.Timestamp('2016-09-13');VAL_END=pd.Timestamp('2016-11-07')
pred=pd.read_csv(O+'predictions.csv.gz',parse_dates=['timestamp']);lab=pd.read_csv(O+'lead_labels.csv.gz',parse_dates=['timestamp'])[['building_id','timestamp','label','in_zero_run']]
info=pd.read_csv(O+'labeled_buildings_info.csv')[['building_id','site_id','primary_use']]
def cutoffs(labels):
    df=pred.merge(labels,on=['building_id','timestamp'],how='left').merge(info,on='building_id',how='left')
    df['label']=df.label.fillna(0).astype(int);df['in_zero_run']=df.in_zero_run.fillna(False).astype(bool)
    df['split']=np.where(df.timestamp<TRAIN_END,'train',np.where(df.timestamp<VAL_END,'val','test'))
    N=['last_hour','typical','A','B','C'];tf=lambda x:np.log1p(np.clip(x,0,None))
    df['valid']=df.meter_reading.notna()&~df.in_zero_run&df[['pred_'+n for n in N]].notna().all(axis=1)
    for n in N: df['err_'+n]=tf(df.meter_reading)-tf(df['pred_'+n])
    cv=df[(df.split=='val')&df.valid&(df.label==0)];ids=pd.Index(sorted(df.building_id.unique()))
    mad=lambda s:(s-s.median()).abs().median()*1.4826
    stats=pd.DataFrame(index=ids);stats['n']=cv.groupby('building_id').size().reindex(ids).fillna(0).astype(int)
    for n in N:
        g=cv.groupby('building_id')['err_'+n];stats['med_'+n]=g.median().reindex(ids);stats['scale_'+n]=np.maximum(g.apply(mad).reindex(ids),0.05)
    stats=stats.join(info.set_index('building_id')[['site_id','primary_use']]);b=stats.n<500;ok=stats[~b]
    for c in [c for c in stats if c.startswith(('med_','scale_'))]:
        bg=ok.groupby(['site_id','primary_use'])[c].median();bs=ok.groupby('site_id')[c].median()
        key=pd.MultiIndex.from_frame(stats[['site_id','primary_use']]);fill=pd.Series(bg.reindex(key).values,index=stats.index).fillna(stats.site_id.map(bs)).fillna(ok[c].median())
        stats.loc[b,c]=fill[b]
    v=df[(df.split=='val')&df.valid].merge(stats[[c for c in stats if c.startswith(('med_','scale_'))]],left_on='building_id',right_index=True)
    cut={}
    for n in N:
        sc=((v['err_'+n]-v['med_'+n]).abs()/v['scale_'+n]).where(v.label==0).dropna()
        cut[n]=float(np.quantile(sc,0.995))
    return cut
ref=json.load(open(O+'cutoffs.json'))['cutoffs'];ref['last_hour']=ref.pop('last_hour')
c0=cutoffs(lab)
print('recomputed cut-offs   :',{k:round(v,4) for k,v in c0.items()})
print('reported cut-offs     :',{k:round(v,4) for k,v in ref.items()})
print('max abs difference    :',max(abs(c0[k]-ref[k]) for k in c0))
lab2=lab.copy();rng=np.random.default_rng(5)
t=lab2.timestamp>=VAL_END;lab2.loc[t,'label']=rng.integers(0,2,t.sum())   # random test labels
c1=cutoffs(lab2)
print('with RANDOM test labels: max abs difference to recomputed =',max(abs(c1[k]-c0[k]) for k in c0),'(must be 0)')
lab3=lab.copy();v=(lab3.timestamp>=TRAIN_END)&(lab3.timestamp<VAL_END);lab3.loc[v,'label']=rng.integers(0,2,v.sum())
c2=cutoffs(lab3)
print('with RANDOM validation labels: max abs difference =',round(max(abs(c2[k]-c0[k]) for k in c0),4),'(may differ: validation labels are used to exclude anomalous hours, as documented)')
# placebo
f=pd.read_csv(O+'flags_ext.csv.gz',parse_dates=['timestamp']);f=f[f.split=='test'].sort_values(['building_id','timestamp']).reset_index(drop=True)
f['t']=(f.timestamp-T0)//pd.Timedelta(hours=1);tmin,tmax=int(f.t.min()),int(f.t.max())
ev=pd.read_csv(O+'lead_events.csv',parse_dates=['start','end']);ev['split']=ev.split.replace({'validation':'val'})
ev=ev[(ev.split=='test')&(ev.zero_share<=0.5)&ev.building_id.isin(f.building_id.unique())].copy()
ev['s']=(ev.start-T0)//pd.Timedelta(hours=1);ev['e']=(ev.end-T0)//pd.Timedelta(hours=1)
vt={b:g.t.to_numpy() for b,g in f[f.valid].groupby('building_id')}
cnt=lambda b,s,e:0 if vt.get(b) is None else int(np.searchsorted(vt[b],e,'right')-np.searchsorted(vt[b],s,'left'))
ev=ev[[cnt(b,s,e)>0 for b,s,e in zip(ev.building_id,ev.s,ev.e)]].reset_index(drop=True)
def flags(m):
    s=f['score_'+m].where(f.valid);p=s.groupby(f.building_id).rank(pct=True,method='first');return (p>0.99).fillna(False).to_numpy()
FL={m:{b:g.t.to_numpy() for b,g in f[flags(m)].groupby('building_id')} for m in ['last_hour','C']}
def rec(m,S,E,B):
    T=FL[m];return np.mean([(b in T) and (np.searchsorted(T[b],e,'right')>np.searchsorted(T[b],s,'left')) for b,s,e in zip(B,S,E)])
B=ev.building_id.to_numpy();S=ev.s.to_numpy();E=ev.e.to_numpy()
print('REAL labels   : last hour %.1f%%, Model C %.1f%% of %d events'%(100*rec('last_hour',S,E,B),100*rec('C',S,E,B),len(ev)))
rng=np.random.default_rng(11);res={'last_hour':[],'C':[]}
span=tmax-tmin+1
for k in range(200):
    off=rng.integers(200,span-200,len(ev))  # random shift (hours), wrapped inside the test period
    S2=tmin+((S-tmin+off)%span);E2=S2+(E-S)
    for m in res: res[m].append(rec(m,S2,E2,B))
for m in res: print('PLACEBO %-9s: mean %.1f%%  max %.1f%%  (200 random shifts)'%(m,100*np.mean(res[m]),100*np.max(res[m])))
