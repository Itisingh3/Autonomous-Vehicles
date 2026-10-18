# Experiment Matrix

| ID | Experiment/question | Variables and baseline | Seeds | Outputs/metrics | Status and claim support |
|---|---|---|---:|---|---|
| E1 | Does handover reduce full V2R latency? | Full exchange vs token; one configured run | 1 | `handover_results.csv`; latency, success, fallback | **Partially completed**; directional only |
| E2 | How do speed/density/spacing/suite/threat affect protocol metrics? | 3 speeds × 6 densities × 2 spacings × 3 suites × 4 malicious rates × 5 attacks; full exchange baseline | 2 actually per group | `final_experiment_results.csv`, summary, figures; all latency/network/security columns | **Partially completed** stochastic development model; not network evidence |
| E3 | Does reputation grouping reduce consensus latency? | Standard PBFT vs reputation PBFT; 13 nodes, f=4, q=9 | 1 C++ row; 2 stochastic rows/group | `pbft_results.csv`, `pbft_comparison.csv` | **Partially completed** |
| E4 | Which reputation parameters affect detection/fairness? | 3 alpha × 3 beta_high × 3 gamma × 3 lambda_recent × 3 W; 10 attack/fault scenarios | 20 per case | `reputation_sensitivity.csv`, grouped CSV, seven plots | **Completed as rule-based Python sensitivity experiment**, not network campaign |
| E5 | Do symbolic models satisfy secrecy/authentication correspondences? | V2R, handover, V2V ideal symbolic primitives | N/A | three `.pv` files; table8 | **Completed symbolically** under assumptions |
| E6 | Does direct/RSU-assisted V2V meet latency/PDR/security targets? | Design specifies modes | **NOT FOUND** | V2V result CSV **NOT FOUND** | **Not completed** |
| E7 | Does real CAV telemetry reproduce results? | Instrumented traces | **NOT FOUND** | Trace files **NOT FOUND** | **Not completed** |

## Matrix arithmetic

The final factorial has 3×6×2×3×4×5 = 2,160 parameter groups and 2 rows per group = 4,320 rows. The reputation matrix has 3×3×3×3×3 = 243 configurations × 10 scenarios × 20 seeds = 48,600 rows.

## Interpretation

The only completed repeated-seed experiment is the rule-based reputation sensitivity sweep, and it is a development model. The principal handover claim has one measured development row and symbolic support, but no paired multi-seed OMNeT++/Veins campaign. Any letter should state these scopes explicitly.
