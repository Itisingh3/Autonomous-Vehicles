# Reproducibility record

Updated 2026-10-18 after the replicated five-RSU campaign.

## Environment

The campaign was run inside WSL distribution `opp_env` using `opp_env run omnetpp-6.0.1`. The executable was `simulation/omnetpp/cav_pqc_network`, with Veins at `/home/opp_env/veins/src`. Exact host hardware details are NOT FOUND in the campaign log.

## Build and campaign commands

From the repository root:

```powershell
wsl.exe -d opp_env -- bash -lc "cd /home/opp_env/cav-pqc-framework/simulation/omnetpp && make MODE=release -j2"
wsl.exe -d opp_env -- bash -lc "cd /home/opp_env/cav-pqc-framework && ./simulation/omnetpp/run_handover_campaign.sh --seeds 20 --speeds 30,50,80 --densities 50,100,200,300 --spacings 250,400 --min-rsus 3"
```

The runner uses paired seed labels and collects 20 valid five-RSU runs per configuration, recording every transition and a per-run log.

## Inputs

- `simulation/omnetpp/omnetpp_validation.ini`
- `simulation/omnetpp/cav-pqc-network.ned`
- `simulation/omnetpp/CAVApp.cc`, `RSUApp.cc`
- `simulation/omnetpp/run_handover_campaign.sh`
- Speeds: 30, 50, 80 km/h; densities: 50, 100, 200, 300; spacing: 250, 400 m.
- Topology: five RSUs and four handover transitions per valid run.

## Outputs

- `results/raw/omnetpp_handover_campaign.csv` — 1,920 successful transition records plus rejected attempts.
- `results/raw/handover_logs/` — per-attempt logs.
- `results/summary/omnetpp_handover_campaign_summary.csv` — mean, median, standard deviation, 95% CI half-width, and n=20.
- Requested figures are in `results/plots/`.

The overhead, throughput, packet-delivery, and per-operation campaign plots are marked NOT FOUND because their raw fields are blank; no values were imputed.

## Verification

```powershell
python -c "import csv,collections; r=list(csv.DictReader(open('results/raw/omnetpp_handover_campaign.csv'))); v=[x for x in r if x['status']=='success']; print(len(v), len(set((x['seed'],x['speed_kmh'],x['density'],x['rsu_spacing_m']) for x in v))); print(collections.Counter(x['transition_index'] for x in v))"
```

Expected validation: 1,920 successful transition rows, 480 unique seed/configuration pairs, and 480 rows for each transition index 1–4. The aggregate CSV reports `valid_seed_count=20`.

## Statistical procedure

For each condition and transition, the interval is descriptive: `mean ± 1.96 × (sample standard deviation / sqrt(n))`. No hypothesis test, p-value, effect-size test, or statistical-significance claim was performed.

## Limitations

This is deterministic OMNeT++ application validation, not real instrumented CAV traffic. The application does not model density- or speed-dependent network effects, so condition values are invariant. Campaign-level cryptographic operation timings, message overhead, PDR, and throughput are unavailable. ProVerif and PBFT artifacts are symbolic and development-model evidence, respectively.
