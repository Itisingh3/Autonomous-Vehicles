#!/usr/bin/env python3
import argparse, csv
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--output',required=True); a=p.parse_args()
    rows=list(csv.DictReader(open(a.input,encoding='utf-8')))
    if not rows: raise SystemExit('empty campaign')
    labels=['full V2R','handover token']; values=[]
    for key in ('full_handshake_latency_ms','handover_latency_ms'):
        vals=[float(r[key]) for r in rows if r.get(key)]
        if not vals: raise SystemExit(f'missing metric {key}')
        values.append(sum(vals)/len(vals))
    Path(a.output).parent.mkdir(parents=True,exist_ok=True)
    plt.figure(figsize=(6,4)); plt.bar(labels,values); plt.ylabel('Latency (ms)'); plt.tight_layout(); plt.savefig(a.output,dpi=180); plt.close()
if __name__=='__main__': main()
