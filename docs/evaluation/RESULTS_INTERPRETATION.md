# Results Interpretation

## Evidence classes

| Class | Files | Interpretation |
|---|---|---|
| One-run development measurements | `handover_results.csv`, `pbft_results.csv` | Concrete recorded rows, but no repeated-seed confidence interval. |
| Stochastic development simulation | `final_experiment_results.csv`, `final_experiment_summary.csv`, `crypto_metrics.csv`, `pbft_comparison.csv`, reputation sensitivity CSVs | Python-generated values labelled `development_stochastic_protocol_model`; not OMNeT++/Veins measurements. |
| Formal | three `.pv` files and `table8_proverif_results.md` | Symbolic verification summaries. |
| Figures/tables | `paper/figures/*`, `paper/tables/*` | Derived presentation artifacts; they do not add evidence beyond their source CSVs. |

## One-run handover result

`results/raw/handover_results.csv` contains one successful row: full V2R latency 0.0183517 s (18.3517 ms), handover latency 0.00503833 s (5.03833 ms), success=1, fallback=0. The arithmetic reduction `(18.3517-5.03833)/18.3517` is 72.55%. This supports a directional proof-of-concept only; a confidence interval, paired seeds, density/speed sweep, and network trace linkage are **NOT FOUND**.

## One-run PBFT result

`pbft_results.csv` reports standard PBFT 36.3343 ms and reputation PBFT 31.0289 ms, with 13 nodes, f=4, quorum=9, 5 requests, and 3 quarantined/3 revoked nodes in the adaptive row. The arithmetic reduction is 14.60%. It is one development run and does not establish a statistically validated network improvement.

## Final factorial CSV

`final_experiment_results.csv` has 4,320 rows, 2,160 parameter groups, and exactly two seeds (42 and 43) per group. Variables are speed 30/50/80, density 50–300, RSU spacing 250/400, three PQC suites, malicious percentage 0/5/10/20, and five attacks. Metrics include full/handover latency, reduction, KEM/DSA operation times, overhead, throughput, PDR, consensus latency, detection, FPR, and FNR. The source column explicitly says `development_stochastic_protocol_model`.

The older `results/summary.md` reports overall means (full 4.2845 ms; handover 1.5399 ms; reduction 64.00%; KEM encap 0.5154 ms; decap 0.4668 ms; DSA sign 0.3699 ms; verify 0.2641 ms; overhead 1211.92 bytes; throughput 143.56 messages/s; PDR .8768; standard consensus 7.3229 ms; reputation 6.4351 ms; detection .9060; FPR .0269; FNR .0983). These figures are development-model aggregates and should be labelled as such. Because n=2 per group, any confidence interval is weak and the older claim of 20 seeds is inconsistent with the CSV.

## Crypto metrics

`crypto_metrics.csv` contains one aggregate row per suite: ML-KEM-512/ML-DSA-44 = 0.4119/0.3736/0.2992/0.2159 ms; ML-KEM-768/ML-DSA-65 = 0.5025/0.4558/0.3530/0.2547 ms; ML-KEM-1024/ML-DSA-87 = 0.6096/0.5530/0.4249/0.3065 ms (encapsulation/decapsulation/sign/verify). These are not independently measured liboqs benchmarks in the current evidence set.

## Reputation sensitivity

`reputation_sensitivity.csv` contains 48,600 rows = 243 parameter combinations × 10 scenarios × 20 seeds. `reputation_sensitivity_summary.csv` contains 2,430 grouped rows. It includes detection/FPR/FNR, quarantine/revocation/recovery time, honest removals, consensus latency, message count, throughput, and a trajectory string. This is the strongest repeated-seed development experiment, but it is Python rule-based simulation, not a consensus-network trace. The one-row smoke CSV is a validation artifact and must not be pooled with the full matrix.

## ProVerif

The recorded table reports V2R 4/4, handover 4/4, and V2V 5/5 queries true. This demonstrates symbolic properties under the model assumptions. It does not prove implementation correctness or quantitative performance.

## Plots and tables

The plots under `paper/figures/` and `results/plots/` visualize the CSV-derived trends: latency, reduction, overhead, throughput, PBFT latency, detection/FPR, and cryptographic metrics. Plot files alone do not provide raw data, confidence intervals, or an independent experiment. Tables 1–8 summarize the same evidence. A plot for a missing metric is **NOT FOUND** rather than evidence that the metric is zero.

## Unsupported or inconsistent points

- A final 20–30-seed network campaign: **NOT SUPPORTED** by the final CSV.
- Real CAV telemetry or Veins/SUMO trace: **NOT FOUND**.
- P-values and effect sizes: **NOT FOUND**.
- Full V2V executable performance campaign: **NOT FOUND**.
- Independent all-suite liboqs wall-clock benchmark: **NOT FOUND**.
- The documented medium invalid-timestamp penalty of -3 conflicts with the Python default medium penalty of -2.
