import pandas as pd, numpy as np
O='/home/claude/rerun/ProjectFull/outputs_full/'
D='/home/claude/rerun/ProjectFull/ashrae-energy-prediction/'
M='C'
f=pd.read_csv(O+'flags_ext.csv.gz',parse_dates=['timestamp'])
f=f[f.split=='test'].sort_values(['building_id','timestamp']).reset_index(drop=True)
pr=pd.read_csv(O+'predictions.csv.gz',parse_dates=['timestamp'])[['building_id','timestamp','meter_reading','pred_C']]
info=pd.read_csv(O+'labeled_buildings_info.csv').set_index('building_id')
w=pd.read_csv(D+'weather_train.csv',parse_dates=['timestamp'])[['site_id','timestamp','air_temperature']]
f=f.merge(pr,on=['building_id','timestamp'],how='left')
f['site_id']=f.building_id.map(info.site_id)
f=f.merge(w,on=['site_id','timestamp'],how='left')
f['t']=(f.timestamp-pd.Timestamp('2016-01-01'))//pd.Timedelta(hours=1)
# site-wide hours (same rule as notebook 10 part B)
g=f[f.valid].groupby(['site_id','timestamp']).agg(nb=('building_id','nunique'),nfl=('flag_C','sum'));g['share']=g.nfl/g.nb
sw=set(g[(g.nb>=3)&(g.share>=.3)].index)
fl=f[f.flag_C].copy()
gap=fl.groupby('building_id')['t'].diff();fl['rid']=(gap.isna()|(gap>1)).cumsum()
lab=f[f.label==1].groupby('building_id')['t'].apply(lambda s:s.to_numpy())
def near(b,s,e):
    a=lab.get(b)
    if a is None or len(a)==0:return np.nan
    i=np.searchsorted(a,s);d=[]
    if i<len(a):d.append(max(0,a[i]-e))
    if i>0:d.append(max(0,s-a[i-1]))
    return min(d)
rows=[]
for rid,r in fl.groupby('rid'):
    b=int(r.building_id.iloc[0]);pk=r.loc[r.score_C.idxmax()]
    s,e=int(r.t.min()),int(r.t.max())
    below=(r.meter_reading<r.pred_C).mean()
    rows.append(dict(building_id=b,site_id=int(info.loc[b,'site_id']),primary_use=info.loc[b,'primary_use'],
      start=r.timestamp.min(),end=r.timestamp.max(),hours=len(r),peak_score=round(pk.score_C,2),
      peak_hour=pk.timestamp,actual_kwh_at_peak=round(pk.meter_reading,1),expected_kwh_at_peak=round(pk.pred_C,1),
      ratio_actual_to_expected=round(pk.meter_reading/max(pk.pred_C,1e-9),2),
      direction='below expected' if below>=0.5 else 'above expected',
      mean_air_temp_c=round(r.air_temperature.mean(),1),
      all_zero=bool((r.meter_reading==0).all()),
      sitewide=any((pk.site_id,t) in sw for t in r.timestamp),
      touches_label=bool(r.label.max()),hours_to_nearest_label=near(b,s,e)))
R=pd.DataFrame(rows).sort_values('peak_score',ascending=False).reset_index(drop=True)
R.insert(0,'rank',R.index+1)
R.to_csv('/home/claude/rerun/t30/ranked_review_list_model_C_test.csv',index=False)
print(len(R),'runs; touching a label',R.touches_label.sum())
for k in (10,25,50,100,200):
    print('top',k,'touch label %.0f%%'%(100*R.head(k).touches_label.mean()),'| all-zero',R.head(k).all_zero.sum(),'| sitewide',R.head(k).sitewide.sum())
print('overall touch label %.1f%%'%(100*R.touches_label.mean()))
print(R.direction.value_counts().to_dict(), 'all_zero',R.all_zero.sum(),'sitewide',R.sitewide.sum())
print(R.head(10)[['rank','building_id','primary_use','start','hours','peak_score','actual_kwh_at_peak','expected_kwh_at_peak','direction','touches_label']].to_string())
