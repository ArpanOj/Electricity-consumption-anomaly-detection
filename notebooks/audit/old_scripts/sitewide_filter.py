import pandas as pd, numpy as np
O='/home/claude/rerun/ProjectFull/outputs_full/'
T0=pd.Timestamp('2016-01-01')
f=pd.read_csv(O+'flags_ext.csv.gz',parse_dates=['timestamp']);f=f[f.split=='test'].sort_values(['building_id','timestamp']).reset_index(drop=True)
info=pd.read_csv(O+'labeled_buildings_info.csv').set_index('building_id');f['site']=f.building_id.map(info.site_id)
f['t']=(f.timestamp-T0)//pd.Timedelta(hours=1)
ev=pd.read_csv(O+'lead_events.csv',parse_dates=['start','end']);ev['split']=ev.split.replace({'validation':'val'})
ev=ev[(ev.split=='test')&(ev.zero_share<=0.5)&ev.building_id.isin(f.building_id.unique())].copy()
ev['s']=(ev.start-T0)//pd.Timedelta(hours=1);ev['e']=(ev.end-T0)//pd.Timedelta(hours=1)
vt={b:g.t.to_numpy() for b,g in f[f.valid].groupby('building_id')}
ev['nv']=[0 if vt.get(b) is None else int(np.searchsorted(vt[b],e,'right')-np.searchsorted(vt[b],s,'left')) for b,s,e in zip(ev.building_id,ev.s,ev.e)]
ev=ev[ev.nv>0].reset_index(drop=True)
def found(mask):
    T={b:g.t.to_numpy() for b,g in f[mask].groupby('building_id')}
    return np.array([(b in T) and (np.searchsorted(T[b],e,'right')>np.searchsorted(T[b],s,'left')) for b,s,e in zip(ev.building_id,ev.s,ev.e)])
def runs(mask):
    x=f[mask];gap=x.groupby('building_id').t.diff();rid=(gap.isna()|(gap>1)).cumsum()
    r=x.groupby(rid).agg(hit=('label','max'));return len(r),int(r.hit.sum())
def site_flags(mask,nmin,share):
    g=f[f.valid].assign(m=mask[f.valid.to_numpy()]).groupby(['site','timestamp']).agg(nb=('building_id','nunique'),nfl=('m','sum'))
    ok=g[(g.nb>=nmin)&(g.nfl/g.nb>=share)].index
    return f.set_index(['site','timestamp']).index.isin(ok)
def rate_mask(col,r):
    s=f[col].where(f.valid);p=s.groupby(f.building_id).rank(pct=True,method='first');return (p>1-r/100).fillna(False).to_numpy()
rows=[]
for meth in ['last_hour','C']:
    for design,base in [('frozen cut-off',f['flag_'+meth].to_numpy()),('1% per building',rate_mask('score_'+meth,1.0))]:
        for nmin,share in [(3,0.30),(3,0.20),(3,0.50),(5,0.30)]:
            sw=site_flags(base,nmin,share)
            kept=base&~sw
            f0=found(base);f1=found(kept);r0=runs(base);r1=runs(kept)
            rows.append(dict(method=meth,design=design,rule=f'>={nmin} buildings, >={int(share*100)}% flagged',
              main_rule=(nmin==3 and share==0.30),
              flagged_hours_before=int(base.sum()),flagged_hours_removed=int((base&sw).sum()),
              share_removed_pct=round(100*(base&sw).sum()/max(1,base.sum()),1),
              labeled_share_of_removed_pct=round(100*f.label[base&sw].mean(),1) if (base&sw).any() else np.nan,
              events_found_before=int(f0.sum()),events_found_after=int(f1.sum()),events_lost=int((f0&~f1).sum()),
              recall_before_pct=round(100*f0.mean(),1),recall_after_pct=round(100*f1.mean(),1),
              runs_before=r0[0],runs_after=r1[0],run_precision_before_pct=round(100*r0[1]/r0[0],1),run_precision_after_pct=round(100*r1[1]/max(1,r1[0]),1)))
R=pd.DataFrame(rows);R.to_csv('sitewide_filter_results.csv',index=False)
pd.set_option('display.width',260,'display.max_columns',30)
print(len(ev),'events');print(R[R.main_rule].drop(columns='main_rule').T.to_string())
print(R[~R.main_rule][['method','design','rule','flagged_hours_removed','events_lost','recall_after_pct','run_precision_after_pct']].to_string())
