"""Leakage test 1 (future perturbation) and 2 (structure). Rebuilds features exactly as notebook 03, fits Model C with frozen settings,
then destroys all readings from CUT onward and checks that predictions before CUT do not change."""
import json,sys,os,time
sys.path.insert(0,'/home/claude/rerun/t39/nb'); os.chdir('/home/claude/rerun/t39/nb')
import numpy as np,pandas as pd
nb=json.load(open('/home/claude/rerun/ProjectFull/notebooks/03_gepiii_predictors.ipynb'));ns={'__name__':'__main__'}
for c in nb['cells']:
    if c['cell_type']!='code': continue
    s=''.join(c['source'])
    if 'models = {}' in s: break
    exec(compile(s,'nb03','exec'),ns)
df=ns['df'];FE=ns['FEATURES'];fit=ns['fit'];BEST=ns['BEST'];train=ns['train_rows']
print('features of C:',FE['C'],flush=True)
forbidden=[c for c in FE['C'] if c in ('y','meter_reading','label','anomaly','split','in_zero_run')]
print('forbidden columns used as features:',forbidden)
print('latest training timestamp:',train.timestamp.max(),'| TRAIN_END',ns['TRAIN_END'],'| all before TRAIN_END:',bool((train.timestamp<ns['TRAIN_END']).all()))
m=fit(FE['C'],BEST,train)
base=m.predict(df[FE['C']])
CUT=pd.Timestamp('2016-12-01')
d2=df.copy()
# CONTROL: recompute lags from the UNPERTURBED readings and compare with the lags stored by notebook 03
c=df.copy();c['ly']=np.log1p(c['y']);gc=c.groupby('building_id')['ly']
for k in (1,24,168):
    nw=gc.shift(k).to_numpy();old=c[f'lag_{k}'].to_numpy();bad=~((np.isnan(nw)&np.isnan(old))|np.isclose(nw,old,equal_nan=False,atol=1e-6))
    print(f'control lag_{k}: rows that differ from stored lag =',int(bad.sum()))
print('control predictions max diff:',np.nanmax(np.abs(m.predict(c.assign(lag_1=gc.shift(1),lag_24=gc.shift(24),lag_168=gc.shift(168))[FE['C']])-base)))
print('is df sorted by building,time:',bool(df.sort_values(['building_id','timestamp']).index.equals(df.index)),flush=True)
rng=np.random.default_rng(1)
fut=d2.timestamp>=CUT
d2.loc[fut,'y']=rng.uniform(0,5000,fut.sum()).astype('float32')   # destroy every reading from 1 Dec onward
d2['ly']=np.log1p(d2['y']);g=d2.groupby('building_id')['ly']
d2['lag_1']=g.shift(1);d2['lag_24']=g.shift(24);d2['lag_168']=g.shift(168)
new=m.predict(d2[FE['C']])
past=(d2.timestamp<CUT).to_numpy()
diff_past=np.nanmax(np.abs(new[past]-base[past]))
diff_fut=np.nanmax(np.abs(new[~past]-base[~past]))
print('max change in predictions BEFORE the cut (must be 0):',diff_past)
print('max change in predictions AFTER the cut (must be >0, shows the test can detect dependence):',diff_fut)
# 1-hour-ahead strictness: prediction at the first hour of CUT must not change (uses only readings before CUT)
first=(d2.timestamp==CUT).to_numpy()
print('max change at exactly the cut hour (uses only past readings; must be 0):',np.nanmax(np.abs(new[first]-base[first])))
