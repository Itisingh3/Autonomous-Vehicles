# Reproducibility package

This document records the commands and environment for the current development artifacts. It does not claim that the current Windows checkout can execute OMNeT++: no `omnetpp`, `opp_run`, SUMO, or compiled `cav_pqc_network` binary is currently on `PATH` or in `simulation/omnetpp`.

## Software versions

The frozen project lockfile (`simulation/versions.lock`) specifies:

| Component | Locked version |
|---|---:|
| OMNeT++ | 6.1.0 |
| Veins | 5.3.1 |
| SUMO | 1.22.0 |
| liboqs | 0.12.0 |
| ProVerif | 2.05 |

The checked-in OMNeT++ README describes an older `opp_env` combination (OMNeT++ 6.0.1, Veins 5.2, SUMO 1.25.0). This is an unresolved environment inconsistency; the lockfile is the reproducibility target and the README commands must be adjusted to the installed toolchain before reporting network measurements.

Python used for this audit: CPython 3.13.5, Windows 11 build 10.0.26200, AMD64, 12 logical CPUs. The sandbox did not expose a reliable physical CPU model or total-memory value; record those manually on the execution host with `Get-CimInstance Win32_Processor` and `Get-CimInstance Win32_ComputerSystem`.

## Rebuild commands

From the project root in PowerShell:

```powershell
python -m py_compile experiments\run_final_experiments.py
python -m pytest -q
```

Inside the compatible `opp_env` shell (paths must match the installed lockfile versions):

```bash
cd simulation/omnetpp
opp_env run omnetpp-6.1.0 -c "make MODE=release -j2"
```

The Makefile expects liboqs under `../../.deps/oqs` and Veins include/library paths supplied by the selected `opp_env` project. Do not silently substitute another liboqs or Veins build.

## Experiment commands

Development factorial sweep (20 seeds per configuration):

```powershell
python experiments\run_final_experiments.py --seeds 20
```

30-seed production sweep:

```powershell
python experiments\run_final_experiments.py --seeds 30
```

Smoke sweep:

```powershell
python experiments\run_final_experiments.py --smoke
```

OMNeT++ deterministic integration check:

```bash
cd simulation/omnetpp
opp_env run omnetpp-6.1.0 -c "./cav_pqc_network -u Cmdenv -n .:../.neddeps -f omnetpp.ini"
```

PBFT development executable:

```bash
cd simulation/pbft
make MODE=release -j2
./pbft_reputation
```

Formal verification:

```powershell
& 'C:\Tools\proverif2.05\proverif.exe' proverif\v2r_handshake.pv
& 'C:\Tools\proverif2.05\proverif.exe' proverif\handover_token.pv
& 'C:\Tools\proverif2.05\proverif.exe' proverif\v2v_session.pv
```

## Regenerating outputs

The factorial command regenerates:

- `results/raw/final_experiment_results.csv`
- `results/raw/final_experiment_summary.csv`
- `results/raw/crypto_metrics.csv`
- `results/raw/pbft_comparison.csv`
- `results/summary.md`
- `results/plots/*.png`
- `paper/tables/*.md`
- `paper/figures/*.png`

The OMNeT++ run writes `results/raw/handover_results.csv`. The PBFT executable writes `results/raw/pbft_results.csv`. ProVerif writes no CSV; its verification summary is read from stdout.

## Seeds and inputs

- Factorial sweep seed start: `42`.
- Default final sweep: seeds `42` through `61` (20 seeds).
- Extended sweep: seeds `42` through `71` (30 seeds).
- Input dimensions: speeds 30/50/80 km/h; densities 50/100/150/200/250/300; RSU spacing 250/400 m; three requested PQC suites; malicious rates 0/5/10/20%; replay, forgery, Sybil, DoS, and false-position attacks.
- Configuration files: `simulation/versions.lock`, `simulation/omnetpp/omnetpp.ini`, `simulation/omnetpp/cav-pqc-network.ned`, `simulation/pbft/Makefile`, and `experiments/run_final_experiments.py`.

## Output locations and expected runtime

| Experiment | Output | Expected runtime |
|---|---|---:|
| Python smoke sweep | CSV/plots/tables above | seconds to minutes |
| Python 20-seed sweep | 43,200 raw rows; 2,160 grouped rows | about 10–30 seconds on this host |
| Python 30-seed sweep | 64,800 raw rows | about 15–45 seconds |
| OMNeT++ deterministic check | `handover_results.csv`, scalar/vector files | seconds to minutes after successful build |
| PBFT C++ development run | `pbft_results.csv` | seconds to minutes, dominated by PQC operations |
| ProVerif models | stdout verification summaries | seconds per model |

## End-to-end handover reproduction status

The recorded artifact was independently checked with:

```powershell
python -c 'import csv; x=next(csv.DictReader(open("results/raw/handover_results.csv"))); f=float(x["full_handshake_latency_s"])*1000; h=float(x["handover_latency_s"])*1000; print("%.5f ms %.5f ms %.2f%% success=%s"%(f,h,(f-h)/f*100,x["handover_success"]))'
```

Observed output:

```text
18.35170 ms 5.03833 ms 72.55% success=1
```

A new end-to-end OMNeT++ reproduction could not be completed in this environment because the required OMNeT++/Veins runtime and compiled `cav_pqc_network` executable were unavailable. Therefore, an independent run matching the recorded handover result is **not confirmed**. The values above are an internal consistency check of the previously recorded CSV, not a new simulation run.

## Known limitations

1. The large factorial sweep is labelled `development_stochastic_protocol_model`; it is not an OMNeT++/Veins network execution.
2. The existing handover and PBFT CSVs are single-run development artifacts and cannot provide confidence intervals.
3. No measured all-suite liboqs benchmark CSV is currently present; factorial cryptographic timings are simulated development values.
4. The README and lockfile specify incompatible OMNeT++/Veins/SUMO combinations and must be reconciled before network evidence is reported.
5. Real CAV traces, paired 20–30-seed network comparisons, p-values, and effect sizes remain outstanding.
