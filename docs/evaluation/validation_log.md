# Validation execution log

Updated: 2026-10-18

| Step | Status | Evidence |
|---|---|---|
| OMNeT++ build | Completed | Five-RSU executable built in WSL with OMNeT++ 6.0.1. |
| Replicated handover campaign | Completed | 24 configurations, 20 valid paired seeds each; 1,920 successful transition records. |
| Five-RSU coverage | Completed | Every valid seed records transitions 1–4: rsu-001 to rsu-002, rsu-002 to rsu-003, rsu-003 to rsu-004, rsu-004 to rsu-005. |
| Handover outcome | Completed for valid runs | Success 100%; fallback 0%. |
| SUMO/Veins realism | Limited | The campaign uses the deterministic application validation topology; it is not real instrumented CAV traffic. |
| liboqs benchmark | Separate evidence | Use results/raw/crypto_benchmark.csv; campaign-level per-operation timings are NOT FOUND. |
| ProVerif | Completed separately | Existing model outputs and verification table remain symbolic evidence only. |
| PBFT | Development-model evidence | No complete PBFT liveness validation is claimed. |

## Campaign command

```powershell
wsl.exe -d opp_env -- bash -lc "cd /home/opp_env/cav-pqc-framework && ./simulation/omnetpp/run_handover_campaign.sh --seeds 20 --speeds 30,50,80 --densities 50,100,200,300 --spacings 250,400 --min-rsus 3"
```

## Campaign result

The campaign reports mean full V2R latency 18.3848 ms, mean handover-token latency 5.0413 ms, and mean descriptive reduction 72.5788%. The reduction range is 72.2861%–72.6136%; the descriptive 95% CI half-width is ±0.0311 percentage points. No statistical-significance test was run.

## Remaining limitations

Message overhead, packet delivery ratio, throughput, and campaign-level ML-KEM/ML-DSA operation timings are blank in the raw CSV and are not claimed. The configured speed and density labels do not produce differentiated network behavior in this deterministic application. There is no real-world CAV trace validation, no side-channel analysis, and no complete PBFT liveness experiment.
