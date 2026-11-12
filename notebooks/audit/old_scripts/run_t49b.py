import time,pickle,numpy as np,pandas as pd
from sklearn.ensemble import IsolationForest
O='/home/claude/rerun/ProjectFull/outputs_full/'
pr=pd.read_csv(O+'predictions.csv.gz',parse_dates=['timestamp']);lab=pd.read_csv(O+'lead_labels.csv.gz',parse_dates=['timestamp'])[['building_id','timestamp','in_zero_run']]
d=pr.merge(lab,on=['building_id','timestamp'],how='left').sort_values(['building_id','timestamp']).reset_index(drop=True)
d['in_zero_run']=d.in_zero_run.fillna(False).astype(bool);d['y']=d.meter_reading.where(~d.in_zero_run)
d['hour']=d.timestamp.dt.hour;d['wk']=(d.timestamp.dt.dayofweek>=5).astype(int)
t0=time.perf_counter();_=d.groupby('building_id')['y'].shift(1);last_t=time.perf_counter()-t0
tr=d[(d.split=='train')&d.y.notna()]
t0=time.perf_counter();med3=tr.groupby(['building_id','hour','wk'])['y'].median();typ_t=time.perf_counter()-t0
size_typ=len(pickle.dumps(med3))
d['ly']=np.log1p(d.y);g=d.groupby('building_id')['ly'];d['d1']=d.ly-g.shift(1);d['d24']=d.ly-g.shift(24)
F=['ly','d1','d24','hour','wk'];fit_t=sc_t=size=0;n=0;nb=0
for b,s in d.groupby('building_id'):
    ok=s[F].notna().all(axis=1);trn=s[ok&(s.timestamp<'2016-09-13')]
    if len(trn)<200: continue
    t0=time.perf_counter();m=IsolationForest(n_estimators=100,max_samples=256,random_state=0).fit(trn[F]);fit_t+=time.perf_counter()-t0
    te=s[ok&(s.split=='test')]
    if len(te)==0: continue
    t0=time.perf_counter();m.score_samples(te[F]);sc_t+=time.perf_counter()-t0
    size+=len(pickle.dumps(m));n+=len(te);nb+=1
rows=[
 dict(method='Same as last hour',features=0,train_seconds=0.0,predict_seconds_all=round(last_t,3),predict_rows=len(d),model_size_MB=0.0,n_trees=0),
 dict(method='Historical typical value',features=3,train_seconds=round(typ_t,2),predict_seconds_all=None,predict_rows=None,model_size_MB=round(size_typ/1e6,3),n_trees=0),
 dict(method='Model A',features=15,train_seconds=39.6,predict_seconds_all=3.51,predict_rows=264000,model_size_MB=10.12,n_trees=600,predict_ms_single_row=7.06),
 dict(method='Model B',features=17,train_seconds=40.5,predict_seconds_all=3.05,predict_rows=264000,model_size_MB=9.79,n_trees=600,predict_ms_single_row=7.55),
 dict(method='Model C',features=18,train_seconds=43.4,predict_seconds_all=3.20,predict_rows=264000,model_size_MB=9.77,n_trees=600,predict_ms_single_row=7.45),
 dict(method=f'Isolation Forest raw ({nb} buildings x 100 trees)',features=5,train_seconds=round(fit_t,1),predict_seconds_all=round(sc_t,2),predict_rows=n,model_size_MB=round(size/1e6,2),n_trees=100*nb)]
R=pd.DataFrame(rows);R.to_csv('complexity_measurements.csv',index=False);print(R.to_string())
