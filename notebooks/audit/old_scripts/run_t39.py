import json,sys,time
sys.path.insert(0,'/home/claude/rerun/t39/nb')
import os; os.chdir('/home/claude/rerun/t39/nb')
nb=json.load(open('/home/claude/rerun/ProjectFull/notebooks/03_gepiii_predictors.ipynb'))
ns={'__name__':'__main__'}
stop=False
for c in nb['cells']:
    if c['cell_type']!='code': continue
    s=''.join(c['source'])
    if 'to_parquet' in s and 'predictor_settings' in s: break   # stop before saving
    exec(compile(s,'nb03','exec'),ns)
import numpy as np, pandas as pd
df=ns['df'];FEAT=ns['FEATURES']['C'];m=ns['models']['C']
val=ns['val_rows'].copy()
y=np.log1p(val['y'])
def err(X): return float(np.sqrt(np.mean((m.predict(X[FEAT])-y)**2)))
base=err(val);print('baseline val RMSLE (C):',round(base,4),'rows',len(val))
groups={'lag_1 (previous hour)':['lag_1'],'lag_24 (same hour yesterday)':['lag_24'],'lag_168 (same hour last week)':['lag_168'],
 'calendar: hour, day of week, weekend':['hour','dow','is_weekend'],
 'building facts: id, site, use, size, age, floors':['bld_idx','site_id','primary_use_code','square_feet','year_built','floor_count'],
 'weather (6 columns)':[c for c in FEAT if c in ('air_temperature','dew_temperature','cloud_coverage','precip_depth_1_hr','sea_level_pressure','wind_speed')],
 'all three lags together':['lag_1','lag_24','lag_168']}
for f in FEAT: groups.setdefault('single: '+f,[f])
rng=np.random.default_rng(0);rows=[]
for name,cols in groups.items():
    inc=[]
    for rep in range(3):
        X=val.copy();idx=rng.permutation(len(X))
        for c in cols: X[c]=X[c].to_numpy()[idx]
        inc.append(err(X)-base)
    rows.append(dict(group=name,features=';'.join(cols),rmsle_increase_mean=round(np.mean(inc),4),rmsle_increase_sd=round(np.std(inc),4),relative_increase_pct=round(100*np.mean(inc)/base,1)))
    print(rows[-1])
R=pd.DataFrame(rows).sort_values('rmsle_increase_mean',ascending=False)
R.insert(0,'baseline_rmsle',round(base,4))
R.to_csv('/home/claude/rerun/t39/permutation_importance_model_C_val.csv',index=False)
# also: does retrained model reproduce saved predictions? compare with saved pred_C on test
pc=pd.read_csv('/home/claude/rerun/ProjectFull/outputs_full/predictions.csv.gz',parse_dates=['timestamp'])[['building_id','timestamp','pred_C']]
t=df[df.split=='test'][['building_id','timestamp','pred_C']].merge(pc,on=['building_id','timestamp'],suffixes=('_new','_saved')).dropna()
print('retrained vs saved pred_C on test: max abs diff',float((t.pred_C_new-t.pred_C_saved).abs().max()),'corr',float(t.pred_C_new.corr(t.pred_C_saved)))
