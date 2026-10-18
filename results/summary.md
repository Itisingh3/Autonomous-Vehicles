# Evidence summary

Updated 2026-10-18 from the replicated five-RSU OMNeT++ campaign.

## OMNeT++/Veins/SUMO measured campaign

The campaign produced 480 valid paired seeds: 20 seeds for each of 24 configurations (30/50/80 km/h × 50/100/200/300 vehicles × 250/400 m). Each valid seed completed four transitions across five RSUs. The raw file contains 1,920 successful transition records and 96 rejected/no-delivery attempts.

Across all valid paired seeds, aggregating the four transitions per seed:

| Metric | Result |
|---|---:|
| Full V2R latency | 18.3848 ms mean |
| Handover-token latency | 5.0413 ms mean |
| Latency reduction | 72.5788% mean |
| 95% CI for reduction | ±0.0311 percentage points |
| Reduction range | 72.2861%–72.6136% |
| Handover success | 100% |
| Fallback rate among valid runs | 0% |

The per-configuration values are recorded in [omnetpp_handover_campaign_summary.csv](summary/omnetpp_handover_campaign_summary.csv). All 24 configurations have n=20 paired seeds and the same measured values. This invariance is a limitation: the current deterministic application does not yet model density- or speed-dependent mobility/network effects, so no sensitivity claim is made.

| Speed (km/h) | Densities (vehicles) | Spacings (m) | n per configuration | Full ms | Handover ms | Reduction | 95% CI | Range |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 30 | 50, 100, 200, 300 | 250, 400 | 20 | 18.3848 | 5.0413 | 72.5788% | ±0.0311 pp | 72.2861–72.6136% |
| 50 | 50, 100, 200, 300 | 250, 400 | 20 | 18.3848 | 5.0413 | 72.5788% | ±0.0311 pp | 72.2861–72.6136% |
| 80 | 50, 100, 200, 300 | 250, 400 | 20 | 18.3848 | 5.0413 | 72.5788% | ±0.0311 pp | 72.2861–72.6136% |

The full per-transition records are in [omnetpp_handover_campaign.csv](raw/omnetpp_handover_campaign.csv). The reported intervals are descriptive 95% confidence intervals using 1.96·SD/√n; no hypothesis test or statistical-significance claim was performed.

## Other evidence classes

| Evidence class | Status | Interpretation |
|---|---|---|
| liboqs benchmark | Separate artifact | Use only the measured operation timings in `results/raw/crypto_benchmark.csv`; they are not inferred from the campaign. |
| ProVerif | Symbolic | Secrecy/authentication/integrity/replay queries are conditional symbolic results, not computational-security or implementation-correctness proofs. |
| PBFT | Development model | Rule-based PBFT results are not complete OMNeT++ liveness or real-network measurements. |
| Assumptions | Explicit | Five-RSU deterministic topology, paired seed labels, and configured sweep labels are used; density/speed effects are not validated by this application. |
| Remaining limitations | Open | No real CAV traces; campaign fields for message overhead, PDR, throughput, and individual ML-KEM/ML-DSA wall-clock operations are NOT FOUND. |
