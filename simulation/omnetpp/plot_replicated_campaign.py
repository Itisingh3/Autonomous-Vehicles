#!/usr/bin/env python3
"""Create campaign figures; missing metrics are marked NOT FOUND, never imputed."""
import argparse, csv
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt

def read(path):
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def metric(rows, name):
    return [(r, float(r['mean'])) for r in rows if r['metric'] == name]

def save_missing(path, title):
    plt.figure(figsize=(6,4)); plt.text(.5,.5,'NOT FOUND in validated campaign CSV',ha='center',va='center',fontsize=12); plt.title(title); plt.axis('off'); plt.tight_layout(); plt.savefig(path,dpi=180); plt.close()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--input',required=True); ap.add_argument('--output-dir',required=True); a=ap.parse_args()
    rows=read(a.input); out=Path(a.output_dir); out.mkdir(parents=True,exist_ok=True)
    # Latency comparison across all 24 configurations.
    full=metric(rows,'full_handshake_latency_s'); token=metric(rows,'handover_token_latency_s')
    if full and token:
        vals=[sum(v for _,v in full)/len(full)*1000, sum(v for _,v in token)/len(token)*1000]
        plt.figure(figsize=(6,4)); plt.bar(['Full V2R','Handover token'],vals); plt.ylabel('Latency (ms)'); plt.tight_layout(); plt.savefig(out/'handover_latency_comparison.png',dpi=180); plt.close()
    else: save_missing(out/'handover_latency_comparison.png','Handover latency comparison')
    # Reduction by each independent variable.
    red=metric(rows,'latency_reduction_percent')
    for col,fn,xlabel,path in [('speed_kmh',lambda x:int(x),'Vehicle speed (km/h)','latency_reduction_vs_speed.png'),('density',lambda x:int(x),'Vehicle density','latency_reduction_vs_density.png'),('rsu_spacing_m',lambda x:int(x),'RSU spacing (m)','latency_reduction_vs_spacing.png')]:
        if not red: save_missing(out/path,'Latency reduction'); continue
        g=defaultdict(list)
        for r,v in red: g[fn(r[col])].append(v)
        xs=sorted(g); ys=[sum(g[x])/len(g[x]) for x in xs]
        plt.figure(figsize=(6,4)); plt.plot(xs,ys,'o-'); plt.xlabel(xlabel); plt.ylabel('Latency reduction (%)'); plt.grid(True,alpha=.3); plt.tight_layout(); plt.savefig(out/path,dpi=180); plt.close()
    succ=metric(rows,'handover_success')
    if succ:
        g=defaultdict(list)
        for r,v in succ: g[(int(r['speed_kmh']),int(r['density']),int(r['rsu_spacing_m']))].append(v)
        labels=[f'{s}/{d}/{sp}' for s,d,sp in sorted(g)]; vals=[100*sum(g[k])/len(g[k]) for k in sorted(g)]
        plt.figure(figsize=(10,4)); plt.bar(range(len(vals)),vals); plt.xticks(range(len(vals)),labels,rotation=90,fontsize=6); plt.ylabel('Success rate (%)'); plt.tight_layout(); plt.savefig(out/'handover_success_rate.png',dpi=180); plt.close()
    else: save_missing(out/'handover_success_rate.png','Handover success rate')
    for name,title in [('message_overhead.png','Communication overhead'),('throughput.png','Throughput'),('packet_delivery_ratio.png','Packet delivery ratio')]:
        save_missing(out/name,title)
if __name__=='__main__': main()
