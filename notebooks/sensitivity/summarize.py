import pandas as pd,json,os,sys
base='/home/claude/rerun/ProjectFull/outputs_full/'
def load(d):
    s=pd.read_csv(d+'eval_summary_test.csv');e=pd.read_csv(d+'eval_equal_rate_summary_test.csv');c=json.load(open(d+'cutoffs.json'))['cutoffs']
    a=s[s.scope=='All labeled buildings'].set_index('method')
    pb=e[e['mode']=='per_building'].set_index('method');pl=e[e['mode']=='pooled'].set_index('method')
    return dict(events=int(a['events'].iloc[0]),
      last_found=int(a.loc['Same as last hour','events_found']),C_found=int(a.loc['Model C (+ previous hour)','events_found']),
      last_pb=pb.loc['Same as last hour','recall_at_1.0%'],C_pb=pb.loc['Model C (+ previous hour)','recall_at_1.0%'],
      B_pb=pb.loc['Model B (+ yesterday, last week)','recall_at_1.0%'],A_pb=pb.loc['Model A (no history)','recall_at_1.0%'],typ_pb=pb.loc['Historical typical value','recall_at_1.0%'],
      last_pl=pl.loc['Same as last hour','recall_at_1.0%'],C_pl=pl.loc['Model C (+ previous hour)','recall_at_1.0%'],
      cut_last=round(c['last_hour'],2),cut_C=round(c['C'],2))
rows={'reported':load(base)}
for n in ['rawscale','floor002','floor010','zr12','zr48']:
    d=f'{n}/out_{n}/'
    if os.path.exists(d+'eval_equal_rate_summary_test.csv'):
        try: rows[n]=load(d)
        except Exception as ex: rows[n]={'error':str(ex)}
R=pd.DataFrame(rows).T;pd.set_option('display.width',250);print(R.to_string());R.to_csv('sensitivity_variants_summary.csv')
