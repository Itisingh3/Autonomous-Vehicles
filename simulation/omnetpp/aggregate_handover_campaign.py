#!/usr/bin/env python3
"""Aggregate the actual five-RSU campaign CSV without inventing metrics."""
import argparse, csv, math, statistics
from collections import defaultdict

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--min-rsus', type=int, default=3)
    args = ap.parse_args()
    with open(args.input, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    valid = [r for r in rows if r.get('status') == 'success']
    if not valid:
        raise SystemExit('no successful campaign rows')
    for r in valid:
        if int(r['rsus_crossed']) < args.min_rsus:
            raise SystemExit(f"invalid crossing count in seed {r['seed']}")
    groups = defaultdict(list)
    for r in valid:
        groups[(r['speed_kmh'], r['density'], r['rsu_spacing_m'], r['handover_transitions'])].append(r)
    metrics = {'full_handshake_latency_s':'full_handshake_latency_s','handover_token_latency_s':'handover_token_latency_s','latency_reduction_percent':'latency_reduction_percent','handover_success':'handover_success','fallback_used':'fallback_used','rsus_crossed':'rsus_crossed','handover_transitions':'handover_transitions','simulated_network_time_s':'simulated_network_time_s','message_overhead_bytes':'message_overhead_bytes','packet_delivery_ratio':'packet_delivery_ratio','throughput_messages_per_second':'throughput_messages_per_second','cryptographic_wall_clock_us':'cryptographic_wall_clock_us','mlkem_encapsulation_us':'mlkem_encapsulation_us','mlkem_decapsulation_us':'mlkem_decapsulation_us','mldsa_signing_us':'mldsa_signing_us','mldsa_verification_us':'mldsa_verification_us'}
    out = []
    for (speed,density,spacing,transition), rs in sorted(groups.items(), key=lambda x: tuple(map(int,x[0]))):
        for metric,col in metrics.items():
            vals=[float(r[col]) for r in rs if r.get(col) not in ('',None,'-1')]
            if not vals: continue
            sd=statistics.stdev(vals) if len(vals)>1 else 0.0
            out.append({'speed_kmh':speed,'density':density,'rsu_spacing_m':spacing,'transition_index':transition,'metric':metric,'mean':statistics.fmean(vals),'median':statistics.median(vals),'stddev':sd,'ci95_halfwidth':1.96*sd/math.sqrt(len(vals)),'valid_seed_count':len(vals)})
    with open(args.output,'w',newline='',encoding='utf-8') as f:
        fields=['speed_kmh','density','rsu_spacing_m','transition_index','metric','mean','median','stddev','ci95_halfwidth','valid_seed_count']
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(out)
if __name__ == '__main__': main()
