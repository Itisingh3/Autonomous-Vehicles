# Minimum Viable Validation Plan

## Purpose and evidence boundary

This plan defines the smallest complete evidence package that could support a networking letter. It replaces the current one-run handover comparison and stochastic development sweep with reproducible OMNeT++/Veins/SUMO executions, standalone liboqs timing, complete ProVerif logs, and paired reputation-PBFT experiments. No numerical claim is considered supported until the corresponding acceptance criteria and output files exist.

## Files to create or modify

### New files

| File | Purpose |
|---|---|
| `simulation/omnetpp/omnetpp_validation.ini` | Multi-RSU validation configurations and parameter sweeps |
| `simulation/sumo/validation.sumocfg` plus route/network XML inputs | 3–5-RSU route and repeatable vehicle traffic |
| `simulation/omnetpp/run_validation.ps1` | Runs all OMNeT++/Veins/SUMO seeds and archives logs |
| `crypto/tests/crypto_benchmark.cpp` or the repository’s standalone benchmark equivalent | Direct liboqs ML-KEM-768/ML-DSA-65 timing |
| `crypto/tests/run_crypto_benchmark.ps1` | Executes 1,000 repetitions per operation |
| `proverif/run_all.ps1` | Runs all three models and preserves complete stdout/stderr |
| `experiments/run_pbft_validation.py` | Paired standard/reputation PBFT validation with 20 seeds |
| `experiments/aggregate_validation_results.py` | Computes means, medians, standard deviations, 95% CIs, and claim tables |
| `docs/evaluation/validation_log.md` | Version, hardware, command, seed, and run-status log |

### Expected modified files

| File | Required change |
|---|---|
| `simulation/omnetpp/omnetpp.ini` | Only if the validation configuration is kept in the existing ini; otherwise leave unchanged. |
| `results/summary.md` | Add validated results only after acceptance criteria pass. |
| `docs/evaluation/RESULT_AUDIT.md` | Replace provisional statuses with evidence-backed statuses. |
| `docs/evaluation/REPRODUCIBILITY.md` | Add exact validation commands and environment information. |

No V2R, V2V, handover, or cryptographic design change is authorized by this plan.

## Experiment V — minimum OMNeT++/Veins/SUMO campaign

### Design

Use a route crossing at least three and preferably five RSUs. One vehicle performs a complete V2R authenticated key establishment at the first RSU. At each subsequent RSU it presents the short-lived handover token and derives a fresh session key. Invalid-token fallback must be exercised in a separate negative case. The campaign varies:

| Factor | Required values |
|---|---|
| Speed | 30, 50, 80 km/h |
| Vehicle density | 50, 100, 200, 300 |
| RSU spacing | 250 m, 400 m |
| Seeds | At least 20 per configuration, seed IDs recorded explicitly |
| RSU count | 3–5 minimum |

The minimum factorial size is `3 × 4 × 2 × 20 = 480` runs before optional attack or PQC-suite factors. The baseline is full V2R authentication at every RSU. The treatment is full V2R only at the first RSU followed by token authentication.

### Metrics

Record per run and per transition:

- full-handshake latency;
- handover-token latency;
- reduction `100*(L_full-L_handover)/L_full`;
- control/application message overhead in bytes;
- handover success rate and fallback count;
- packet delivery ratio;
- throughput;
- cryptographic wall-clock time separately from simulated network time.

### Commands

From the repository root in a compatible `opp_env` shell:

```bash
cd simulation/omnetpp
opp_env run omnetpp-6.1.0 -c "make MODE=release -j2"
opp_env run omnetpp-6.1.0 -c "powershell -ExecutionPolicy Bypass -File run_validation.ps1"
```

If the launcher is implemented as a direct executable loop, the equivalent command must be recorded in `validation_log.md`, for example:

```powershell
.\cav_pqc_network.exe -u Cmdenv -n .;..\..\simulation\veins\src -f omnetpp_validation.ini -r 0
```

The exact executable and NED path must be verified on the host before the campaign; an assumed command is not evidence.

### Expected outputs

- `results/raw/omnetpp_validation_runs.csv`
- `results/raw/omnetpp_validation_transitions.csv`
- `results/raw/omnetpp_validation_summary.csv`
- `results/raw/omnetpp_validation_logs/`
- `results/plots/validation_latency_by_speed.png`
- `results/plots/validation_latency_by_density.png`
- `results/plots/validation_pdr_throughput.png`

### Runtime estimate

**NOT FOUND before a pilot run.** A 10-run pilot must be timed first. The full estimate is `480 × measured median run time`, plus compilation and SUMO startup overhead.

### Acceptance criteria

1. At least 480 completed runs, with 20 distinct seeds per speed/density/spacing configuration.
2. Every run contains first-RSU full authentication and at least two subsequent RSU transitions.
3. Success, fallback, latency, overhead, PDR, and throughput fields are non-null.
4. Baseline and token treatment use identical mobility, density, spacing, and seed tuples.
5. The summary reports mean, median, standard deviation, and 95% CI.
6. No row is labelled as measured unless it originates from the simulator output.

## Experiment C — standalone liboqs benchmark

### Design

Run ML-KEM-768 key generation, encapsulation, and decapsulation, and ML-DSA-65 key generation, signing, and verification. Use at least 1,000 repetitions per operation after a documented warm-up. Record hardware, compiler, liboqs version, operation success, and timing unit.

### Commands

```powershell
cmake -S crypto/tests -B crypto/tests/build
cmake --build crypto/tests/build --config Release
crypto\tests\build\Release\crypto_benchmark.exe --kem ML-KEM-768 --dsa ML-DSA-65 --repetitions 1000 --output results\raw\crypto_benchmark.csv
```

The command is a required interface for the benchmark implementation; if the build system uses Make instead, the final command must be recorded verbatim in `validation_log.md`.

### Expected output

`results/raw/crypto_benchmark.csv` with one row per operation and at least:

`algorithm,operation,repetitions,mean_us,median_us,stddev_us,ci95_low_us,ci95_high_us,success_count,hardware,liboqs_version`

### Runtime estimate

**NOT FOUND before execution.** It should be measured from command start to completion; 6,000 operations plus key setup is expected to be substantially shorter than the network campaign, but no number is assumed.

### Acceptance criteria

1. Six operation classes are present and each has at least 1,000 successful repetitions.
2. Mean, median, standard deviation, and 95% CI are calculated from raw repetitions, not synthetic factors.
3. The CSV records exact liboqs, compiler, CPU, and operating-system information.
4. No values are copied from `crypto_metrics.csv` unless independently reproduced.

## Experiment P — minimum ProVerif validation

### Commands

```powershell
New-Item -ItemType Directory -Force results\raw\proverif | Out-Null
proverif proverif\v2r_handshake.pv *> results\raw\proverif\v2r_handshake.out.txt
proverif proverif\handover_token.pv *> results\raw\proverif\handover_token.out.txt
proverif proverif\v2v_session.pv *> results\raw\proverif\v2v_session.out.txt
```

### Expected outputs

- `results/raw/proverif/v2r_handshake.out.txt`
- `results/raw/proverif/handover_token.out.txt`
- `results/raw/proverif/v2v_session.out.txt`
- `results/raw/proverif/verification_table.csv`

The table must contain model name, query text, result, command, ProVerif version, and assumptions. The models currently state ideal symbolic ML-KEM/ML-DSA, registered keys, protected RSU channel where applicable, and executable freshness checks as assumptions.

### Acceptance criteria

1. All three models run to completion with no parser or runtime error.
2. Every query is copied into the machine-readable table with its actual result.
3. Secrecy, authentication, and integrity claims are limited to the exact queries present.
4. Outputs are retained; a prose “4/4” summary alone is insufficient.

## Experiment R — minimum reputation-PBFT validation

### Design

Run standard PBFT and reputation-based PBFT on identical node, workload, attack, and seed tuples for at least 20 seeds. Include honest, suspicious, quarantined, and revoked lifecycle cases, plus temporary-fault recovery. Use the configurable recent/long-term sliding-window model and record all parameters.

### Commands

```powershell
python experiments\run_pbft_validation.py --seeds 20 --output results\raw\pbft_validation.csv
python experiments\aggregate_validation_results.py --input results\raw\pbft_validation.csv --output results\summary\pbft_validation_summary.csv
```

### Metrics and expected outputs

- consensus latency;
- consensus messages per transaction;
- detection rate;
- false-positive rate;
- recovery time;
- quarantine and revocation time;
- lifecycle state counts;
- reputation trajectory.

Expected files:

- `results/raw/pbft_validation.csv`
- `results/summary/pbft_validation_summary.csv`
- `results/plots/pbft_validation_latency.png`
- `results/plots/pbft_detection_recovery.png`

### Runtime estimate

**NOT FOUND before execution.** Estimate after a 20-seed smoke run; the full run must record wall-clock duration.

### Acceptance criteria

1. Standard and reputation modes use paired seeds and identical workloads.
2. At least 20 seeds exist for every reported comparison.
3. Honest temporary faults can recover; critical confirmed attacks cannot silently recover.
4. Revocation records show the required distributed confirmation threshold.
5. Metrics are derived from event-level records, not manually entered summary values.

## Evidence-to-claim mapping

| Planned letter claim | Required supporting experiment/file | Status before plan |
|---|---|---|
| Token re-authentication lowers latency | OMNeT++ transition CSV and paired summary | One development row only |
| Benefit persists across speed, density, spacing | `omnetpp_validation_summary.csv` and plots | **NOT SUPPORTED** |
| PQC operation cost is measured | `crypto_benchmark.csv` | Independent benchmark **NOT FOUND** |
| Session/authentication properties hold symbolically | ProVerif output files and verification table | Summary exists; complete outputs **NOT FOUND** |
| Reputation grouping reduces consensus cost | Paired `pbft_validation.csv` and summary | Existing one-run/stochastic evidence only |
| Reputation detects attacks with bounded false positives | Event-level PBFT validation CSV | Existing model sensitivity only |
| V2R/V2V confidentiality and integrity | ProVerif models plus executable tests | V2V network evidence **NOT FOUND** |
| Network PDR/throughput remain acceptable | OMNeT++/Veins summary CSV | **NOT SUPPORTED** |

## Claims that remain unsupported until completion

- A statistically validated percentage latency reduction.
- Real multi-RSU CAV performance.
- Generalization to real traffic or instrumented CAV traces.
- Independent concrete ML-KEM/ML-DSA execution costs.
- PBFT throughput, recovery, or attack-detection guarantees.
- Computational security, forward secrecy under compromise, or implementation correctness from ProVerif.

## Final acceptance gate

The networking letter may use numerical network claims only after Experiments V and C pass their criteria, all ProVerif outputs are archived, Experiment R passes paired-seed criteria, and `RESULT_AUDIT.md` maps each claim to an exact output file. Until then, the letter should be limited to the protocol design, symbolic results, and explicitly provisional development evidence.
