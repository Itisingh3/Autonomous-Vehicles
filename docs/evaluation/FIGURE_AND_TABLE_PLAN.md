# Figure and Table Plan for a Networking Letter

The letter should use no more than four figures and five tables. Only existing data sources are recommended.

## Figures

| Figure | Title/question | Axes | Source/existence | Interpretation |
|---|---|---|---|---|
| 1 | Full V2R versus handover-token latency | x: method; y: ms | `handover_results.csv`; exists, one run | Directly shows the proof-of-concept latency difference; label as one-run development evidence. |
| 2 | Handover reduction across density/speed | x: density or speed; y: reduction % | `final_experiment_results.csv`; exists, n=2/group | Shows stochastic sensitivity, not real mobility performance. |
| 3 | Reputation detection/FPR trade-off | x: beta_high or attack; y: rate | reputation sensitivity CSV/plots; exists, n=20/case | Shows rule-based sensitivity and false-positive behavior. |
| 4 | Symbolic verification and crypto cost summary | x: suite/model; y: ms or verified-query count | `crypto_metrics.csv`, `table8_proverif_results.md`; exists | Combines separate evidence classes only if panels are clearly labelled. |

## Tables

| Table | Title | Columns/source | Exists? |
|---|---|---|---|
| 1 | Protocol and simulation parameters | speed, density, spacing, token validity, skew, 802.11p; ini/scripts | Yes, but missing coverage/warm-up values |
| 2 | PQC operation and suite results | suite, KEM encap/decap, DSA sign/verify; `crypto_metrics.csv` | Yes; stochastic aggregate |
| 3 | V2R/handover comparison | full, token, reduction, success, fallback; handover CSV | Yes; one row |
| 4 | Reputation/PBFT results | mode, CN, f, quorum, latency, lifecycle counts; PBFT CSV and sensitivity summary | Yes; separate evidence classes needed |
| 5 | Formal verification scope | model, entities, queries, outcome, assumptions; ProVerif files/table8 | Yes; symbolic only |

## Do not include

Do not include a figure implying real PDR/throughput validation, a confidence interval from a single handover row, or a 20-seed final factorial claim. Those data are either incomplete or explicitly stochastic development outputs.
