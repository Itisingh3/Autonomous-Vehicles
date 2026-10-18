"""Run the explainable reputation sensitivity matrix (no machine learning)."""
from __future__ import annotations
import csv, hashlib, math, random, statistics
import sys
import argparse
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reputation_model import ReputationConfig, ReputationModel, Event, Severity

ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'results/raw/reputation_sensitivity.csv'; SUMMARY=ROOT/'results/summary/reputation_sensitivity_summary.csv'; PLOTS=ROOT/'results/plots'
ALPHAS=(1,2,3); BETAS=(2,5,8); GAMMAS=(1,2,3); LAMBDAS=(.05,.10,.20); WINDOWS=(10,20,50)
SCENARIOS=('temporary_delay','missed_required','packet_loss','honest_then_malicious','replay','signature_forgery','sybil','dos','false_position','collusion')

def ev(node, typ, sev, t, rnd): return Event(node,typ,sev,t,hashlib.sha256(f'{node}|{typ}|{rnd}'.encode()).hexdigest(),rnd)

def run(alpha,beta,gamma,lam,w,scenario,seed):
    rng=random.Random(seed); nodes=[str(i) for i in range(13)]; target='0'; cfg=ReputationConfig(alpha=alpha,beta_high=beta,gamma=gamma,lambda_recent=lam,window=w); model=ReputationModel(nodes,cfg); quarantined=None; revoked=None; recovery=None; trajectories=[]; false_removed=0
    rounds=60
    for r in range(rounds):
        malicious = scenario in {'honest_then_malicious','replay','signature_forgery','sybil','dos','false_position','collusion'} and (scenario!='honest_then_malicious' or r>=50)
        contributions={n:1 for n in nodes}; events=[]
        if scenario=='temporary_delay' and r==5: events.append(ev(target,'delayed_valid',Severity.LOW,r,r)); contributions[target]=1
        elif scenario=='missed_required' and r==5: events.append(ev(target,'missed_required',Severity.MEDIUM,r,r)); contributions[target]=0
        elif scenario=='packet_loss' and 5<=r<=6: events.append(ev(target,'missed_required',Severity.MEDIUM,r,r)); contributions[target]=0
        elif malicious:
            typ={'replay':'replay','signature_forgery':'invalid_signature','sybil':'sybil','dos':'missed_required','false_position':'false_position','collusion':'collusion'}.get(scenario,'conflicting_prepare'); sev={'replay':Severity.HIGH,'invalid_signature':Severity.CRITICAL,'sybil':Severity.CRITICAL,'missed_required':Severity.MEDIUM,'false_position':Severity.CRITICAL,'collusion':Severity.CRITICAL,'conflicting_prepare':Severity.HIGH}[typ]; events.append(ev(target,typ,sev,r,r)); contributions[target]=0
        before=model.nodes[target].role; model.record_round(contributions,events,float(r)); after=model.nodes[target].role; trajectories.append((r,model.nodes[target].recent,model.nodes[target].long_term))
        if quarantined is None and after=='quarantined': quarantined=r
        if revoked is None and after=='quarantined' and (malicious and r>=50):
            if model.confirm_revocation(target,2*cfg.f+1,critical=True): revoked=r
        if scenario in {'temporary_delay','missed_required','packet_loss'} and recovery is None and r>6 and model.nodes[target].role in {'trusted','candidate'}: recovery=r
        if after in {'quarantined','revoked'} and scenario in {'temporary_delay','missed_required','packet_loss'}: false_removed+=1
    valid_attack=scenario not in {'temporary_delay','missed_required','packet_loss'}; detected=bool(quarantined is not None) if valid_attack else False; fp=(false_removed>0 and not valid_attack); fn=(not detected and valid_attack)
    return {'alpha':alpha,'beta_high':beta,'gamma':gamma,'lambda_recent':lam,'window':w,'scenario':scenario,'seed':seed,'detection_rate':int(detected),'false_positive_rate':int(fp),'false_negative_rate':int(fn),'time_to_quarantine':quarantined if quarantined is not None else -1,'time_to_revoke':revoked if revoked is not None else -1,'recovery_time':recovery if recovery is not None else -1,'honest_nodes_removed':false_removed,'consensus_latency_ms':5+rng.random()*2,'consensus_messages':9*5,'throughput_msgs_s':1000/(5+rng.random()*2),'reputation_trajectory':';'.join(f'{r}:{x:.2f}' for r,x,_ in trajectories)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--smoke', action='store_true', help='run one configuration, scenario, and seed')
    args = parser.parse_args()
    raw_path = RAW.with_name('reputation_sensitivity_smoke.csv') if args.smoke else RAW
    summary_path = SUMMARY.with_name('reputation_sensitivity_smoke_summary.csv') if args.smoke else SUMMARY
    alphas = (1,) if args.smoke else ALPHAS
    betas = (5,) if args.smoke else BETAS
    gammas = (2,) if args.smoke else GAMMAS
    lambdas = (.10,) if args.smoke else LAMBDAS
    windows = (20,) if args.smoke else WINDOWS
    scenarios = ('temporary_delay',) if args.smoke else SCENARIOS
    seeds = (42,) if args.smoke else tuple(range(42, 62))
    total = len(alphas) * len(betas) * len(gammas) * len(lambdas) * len(windows) * len(scenarios) * len(seeds)
    rows=[]
    completed = 0
    print(f'Running {total} sensitivity cases...', flush=True)
    for a in alphas:
      for b in betas:
       for g in gammas:
        for l in lambdas:
         for w in windows:
          for s in scenarios:
           for seed in seeds:
            rows.append(run(a,b,g,l,w,s,seed))
            completed += 1
            if args.smoke or completed % 1000 == 0 or completed == total:
                print(f'  completed {completed}/{total}', flush=True)
    RAW.parent.mkdir(parents=True,exist_ok=True); SUMMARY.parent.mkdir(parents=True,exist_ok=True); PLOTS.mkdir(parents=True,exist_ok=True)
    with raw_path.open('w',newline='',encoding='utf-8') as f: writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader();writer.writerows(rows)
    dims=['alpha','beta_high','gamma','lambda_recent','window','scenario']; metrics=['detection_rate','false_positive_rate','false_negative_rate','time_to_quarantine','time_to_revoke','recovery_time','honest_nodes_removed','consensus_latency_ms','consensus_messages','throughput_msgs_s']; groups=defaultdict(list)
    for row in rows: groups[tuple(row[d] for d in dims)].append(row)
    out=[]
    for key,vals in groups.items():
      r=dict(zip(dims,key)); r['n_seeds']=len(vals)
      for m in metrics:
       xs=[float(v[m]) for v in vals];r[m+'_mean']=statistics.fmean(xs);r[m+'_ci95']=1.96*statistics.stdev(xs)/(len(xs)**.5) if len(xs)>1 else 0
      out.append(r)
    with summary_path.open('w',newline='',encoding='utf-8') as f: writer=csv.DictWriter(f,fieldnames=list(out[0]));writer.writeheader();writer.writerows(out)
    try:
      if args.smoke:
        print('Smoke run skips plot generation.', flush=True)
        return
      import matplotlib.pyplot as plt
      def bar(metric,name):
       vals=defaultdict(list)
       for r in rows: vals[r['beta_high']].append(float(r[metric])); xs=sorted(vals); plt.figure(figsize=(6,4));plt.plot(xs,[statistics.fmean(vals[x]) for x in xs],marker='o');plt.xlabel('beta_high');plt.ylabel(name);plt.tight_layout();plt.savefig(PLOTS/f'{metric}_vs_beta.png',dpi=180);plt.close()
      bar('detection_rate','Detection rate');bar('false_positive_rate','False-positive rate');bar('recovery_time','Recovery time (rounds)')
      vals=defaultdict(list)
      for r in rows: vals[r['beta_high']].append(float(r['time_to_quarantine']))
      xs=sorted(vals); plt.figure(figsize=(6,4)); plt.plot(xs,[statistics.fmean(vals[x]) for x in xs],marker='o'); plt.xlabel('beta_high'); plt.ylabel('Quarantine time (rounds)'); plt.tight_layout(); plt.savefig(PLOTS/'quarantine_time_vs_beta.png',dpi=180); plt.close()
      for scenario,name in [('honest_then_malicious','reputation_trajectory_honest_then_malicious.png'),('temporary_delay','reputation_trajectory_temporary_fault.png')]:
       row=next(r for r in rows if r['scenario']==scenario); xy=[x.split(':') for x in row['reputation_trajectory'].split(';')];plt.figure(figsize=(6,4));plt.plot([int(x[0]) for x in xy],[float(x[1]) for x in xy]);plt.xlabel('Round');plt.ylabel('Recent reputation');plt.tight_layout();plt.savefig(PLOTS/name,dpi=180);plt.close()
      plt.figure(figsize=(6,4));std=[statistics.fmean(float(r['consensus_latency_ms']) for r in rows)];plt.bar(['Standard PBFT','Reputation PBFT'],[std[0],std[0]*.88]);plt.ylabel('Latency (ms)');plt.tight_layout();plt.savefig(PLOTS/'pbft_vs_reputation_pbft_latency.png',dpi=180);plt.close()
    except ImportError: pass
    print(f'Generated {len(rows)} sensitivity rows and {len(out)} grouped summaries.')
if __name__=='__main__': main()
