import json,sys,time,pickle,os
sys.path.insert(0,'/home/claude/rerun/t39/nb'); os.chdir('/home/claude/rerun/t39/nb')
import numpy as np, pandas as pd
nb=json.load(open('/home/claude/rerun/ProjectFull/notebooks/03_gepiii_predictors.ipynb'))
ns={'__name__':'__main__'}
for c in nb['cells']:
    if c['cell_type']!='code': continue
    s=''.join(c['source'])
    if 'to_parquet' in s and 'predictor_settings' in s: break
    exec(compile(s,'nb03','exec'),ns)
df=ns['df'];FEAT=ns['FEATURES'];models=ns['models'];BEST=ns['BEST'];fit=ns['fit'];train_rows=ns['train_rows']
test=df[(df.split=='test')]
rows=[]
import os as _o
print('CPU count',_o.cpu_count(),flush=True)
for k in 'ABC':
    f=FEAT[k]
    t0=time.perf_counter();m=fit(f,BEST,train_rows);tr=time.perf_counter()-t0
    X=test[f]
    t0=time.perf_counter();p=m.predict(X);pr=time.perf_counter()-t0
    X1=X.iloc[:1000]
    t0=time.perf_counter()
    for i in range(200): m.predict(X1.iloc[i:i+1])
    one=(time.perf_counter()-t0)/200
    rows.append(dict(method=f'Model {k}',features=len(f),train_rows=len(train_rows),train_seconds=round(tr,1),predict_rows=len(X),predict_seconds_all=round(pr,2),predict_microsec_per_row_batch=round(pr/len(X)*1e6,1),predict_ms_single_row=round(one*1e3,2),model_size_MB=round(len(pickle.dumps(m))/1e6,2),n_trees=int(m.n_iter_)))
    print(rows[-1],flush=True)
# simple rules
t0=time.perf_counter();_=df.groupby('building_id')['y'].shift(1);rows.append(dict(method='Same as last hour',train_seconds=0,predict_seconds_all=round(time.perf_counter()-t0,3),model_size_MB=0))
tr=df[(df.split=='train')&df.y.notna()]
t0=time.perf_counter();med3=tr.groupby(['building_id','hour','is_weekend'])['y'].median();ft=time.perf_counter()-t0
rows.append(dict(method='Historical typical value',train_seconds=round(ft,2),model_size_MB=round(len(pickle.dumps(med3))/1e6,2),n_trees=None))
# isolation forest, raw variant, per building
from sklearn.ensemble import IsolationForest
d=df.sort_values(['building_id','timestamp']).copy();d['ly']=np.log1p(d.y);g=d.groupby('building_id')['ly']
d['d1']=d.ly-g.shift(1);d['d24']=d.ly-g.shift(24);d['wk']=(d.timestamp.dt.dayofweek>=5).astype(int)
F=['ly','d1','d24','hour','wk'];fit_t=0;sc_t=0;size=0;n=0
for b,s in d.groupby('building_id'):
    ok=s[F].notna().all(axis=1);trn=s[ok&(s.timestamp<'2016-09-13')]
    if len(trn)<200: continue
    t0=time.perf_counter();m=IsolationForest(n_estimators=100,max_samples=256,random_state=0).fit(trn[F]);fit_t+=time.perf_counter()-t0
    te=s[ok&(s.split=='test')]
    t0=time.perf_counter();m.score_samples(te[F]);sc_t+=time.perf_counter()-t0
    size+=len(pickle.dumps(m));n+=len(te)
rows.append(dict(method='Isolation Forest (raw, 200 buildings)',train_seconds=round(fit_t,1),predict_seconds_all=round(sc_t,2),predict_rows=n,model_size_MB=round(size/1e6,2),n_trees=100))
pd.DataFrame(rows).to_csv('/home/claude/rerun/t49/complexity_measurements.csv',index=False)
print(pd.DataFrame(rows).to_string())
import platform;print(platform.platform(),platform.processor())
