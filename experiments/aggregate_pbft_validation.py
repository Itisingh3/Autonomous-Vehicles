#!/usr/bin/env python3
import argparse,csv,math,statistics
from collections import defaultdict
def main():
 p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args(); rows=list(csv.DictReader(open(a.input,encoding='utf-8'))); groups=defaultdict(list)
 for r in rows: groups[(r['mode'],r['scenario'])].append(r)
 out=[]
 for (mode,scenario), vals in groups.items():
  r={'mode':mode,'scenario':scenario,'n_seeds':len(vals)}
  for m in ('consensus_latency_ms','consensus_messages_per_transaction','detection_rate','false_positive_rate','false_negative_rate','time_to_quarantine','time_to_revoke','recovery_time'):
   xs=[float(v[m]) for v in vals]; r[m+'_mean']=statistics.fmean(xs); r[m+'_ci95']=1.96*statistics.stdev(xs)/math.sqrt(len(xs)) if len(xs)>1 else 0
  out.append(r)
 with open(a.output,'w',newline='',encoding='utf-8') as f: w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
 print(f'Wrote {len(out)} PBFT summaries to {a.output}')
if __name__=='__main__': main()
