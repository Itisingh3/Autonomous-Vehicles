# Result audit

Updated 2026-10-18 using only the completed campaign artifacts.

## Evidence classification

| Class | Evidence | Interpretation |
|---|---|---|
| OMNeT++/Veins/SUMO measured | `results/raw/omnetpp_handover_campaign.csv`, `results/summary/omnetpp_handover_campaign_summary.csv` | 480 valid paired seeds, four transitions per seed, five-RSU deterministic topology. |
| liboqs measured | `results/raw/crypto_benchmark.csv` | Independent cryptographic benchmark; not a network-latency measurement. |
| ProVerif symbolic | `results/raw/proverif/*.out.txt`, `verification_table.csv` | Conditional symbolic verification; no computational-security claim. |
| Development PBFT | `results/raw/pbft_results.csv`, PBFT summaries | Rule-based development model; no complete PBFT liveness validation. |

## Campaign audit

- Valid paired seeds: **480 total**, exactly **20 per each of 24 configurations**.
- Valid transitions: **1,920**, covering `rsu-001→002`, `002→003`, `003→004`, and `004→005`.
- Full V2R latency: **18.3848 ms mean**.
- Handover-token latency: **5.0413 ms mean**.
- Latency reduction: **72.5788% mean**, descriptive 95% CI **±0.0311 percentage points**, range **72.2861%–72.6136%**.
- Handover success: **100%** for valid runs; fallback: **0%** for valid runs.
- The interval is `mean ± 1.96·SD/√n`; no p-value, hypothesis test, or statistical-significance claim was produced.

The 24 configuration combinations are separately represented in the aggregate CSV. Their values are invariant because the current deterministic application does not implement density- or speed-dependent mobility/network behavior. This supports the handover path under the tested topology, but does not support a claim that performance changes with speed or density.

## Final claims table

| Claim | Evidence file | Metric | Result | Support level | Safe paper wording |
|---|---|---|---|---|---|
| Handover-token re-authentication is faster than full V2R establishment in the tested topology | `results/raw/omnetpp_handover_campaign.csv` | Latency, paired seeds | 18.3848 ms vs 5.0413 ms; 72.5788% descriptive reduction | Fully supported for this deterministic campaign | “In the five-RSU OMNeT++ validation topology, token re-authentication had lower measured latency than the initial full V2R exchange.” |
| The result is replicated | `results/summary/omnetpp_handover_campaign_summary.csv` | Valid paired seeds | 20 per configuration; 24 configurations | Fully supported | “The comparison was replicated over 20 paired seeds per configured condition.” |
| Handover succeeds through four transitions | `results/raw/omnetpp_handover_campaign.csv` | Success/fallback | 1,920/1,920 successful transition records; no fallback in valid runs | Fully supported for the tested topology | “All valid deterministic runs completed the four configured RSU transitions without fallback.” |
| Performance varies with speed/density/spacing | Campaign CSV/summary | Per-condition latency | NOT FOUND; values are invariant | Unsupported | Do not make this claim. |
| Real-world CAV traces validate the mechanism | None | Real traces | NOT FOUND | Unsupported | Do not make this claim. |
| Message overhead, PDR, and throughput are measured | Campaign CSV | Network metrics | NOT FOUND (fields blank) | Unsupported | Do not make this claim. |
| ML-KEM/ML-DSA operation costs are measured by this campaign | Campaign CSV | Per-operation wall-clock time | NOT FOUND | Unsupported; use independent benchmark only | “Independent liboqs benchmarks are reported separately.” |
| ProVerif proves computational security | ProVerif outputs | Symbolic queries | Symbolic results only | Unsupported | “ProVerif verifies the stated properties under its symbolic assumptions.” |
| PBFT liveness is completely validated | PBFT development outputs | Liveness | NOT FOUND | Unsupported | Do not make this claim. |
| Side-channel resistance is established | None | Side-channel analysis | NOT FOUND | Unsupported | Do not make this claim. |

## Remaining limitations

The campaign is a deterministic OMNeT++ application validation rather than a real instrumented CAV trace campaign. Density and speed are configuration labels whose network effects are not represented in the current application. Campaign-level cryptographic wall-clock and network metrics are absent. The PBFT evidence remains a development model, and ProVerif results remain symbolic rather than computational or implementation proofs.
