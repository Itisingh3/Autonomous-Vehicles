#!/usr/bin/env python3
"""Validate that simulator logs contain required handover transitions."""
import argparse, csv, re, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser(); p.add_argument('--input',required=True); p.add_argument('--output',required=True); a=p.parse_args()
    rows=list(csv.DictReader(open(a.input, newline='', encoding='utf-8')))
    if not rows or any(r['status']!='success' for r in rows): raise SystemExit('campaign contains failed runs')
    out=[]
    for r in rows:
        transitions=int(r.get('transition_count','0') or 0)
        if transitions < 2:
            raise SystemExit(f"{r['log']} demonstrates {transitions} handover transition(s); minimum is 2")
        if not r.get('full_handshake_latency_s') or not r.get('handover_latency_s'):
            raise SystemExit(f"{r['log']} has no latency measurements")
        r['full_handshake_latency_ms']=float(r['full_handshake_latency_s'])*1000
        r['handover_latency_ms']=float(r['handover_latency_s'])*1000
        r['latency_reduction_pct']=100*(r['full_handshake_latency_ms']-r['handover_latency_ms'])/r['full_handshake_latency_ms']
        r['handover_transitions']=transitions; out.append(r)
    with open(a.output,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
if __name__=='__main__': main()
