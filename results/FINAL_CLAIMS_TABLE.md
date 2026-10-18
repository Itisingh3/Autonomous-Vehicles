# Final Claims Table

Only repository evidence is used. Percentages are shown only where both compared values are present in the same result artifact. No statistical significance is claimed without a reported test.

| Claim | Evidence file | Metric | Result | Support level | Safe paper wording |
|---|---|---|---|---|---|
| Handover-token authentication reduces re-authentication latency | `results/raw/handover_results.csv` | Latency, one pilot | 18.3647 ms full vs 5.03833 ms handover; 72.5651% lower | Partially supported | “A single native OMNeT++ pilot measured a 72.5651% latency reduction; replicated multi-RSU validation remains outstanding.” |
| V2R establishes matching session keys | `results/raw/handover_results.csv`; `results/raw/proverif/v2r_handshake.out.txt` | Success flag; symbolic queries | Pilot success=1; V2R model 4/4 true | Partially supported | “The pilot completed the V2R exchange and the symbolic model verifies modeled session correspondence.” |
| V2V establishes secure session keys | `results/raw/proverif/v2v_session.out.txt` | Symbolic secrecy/authentication/integrity | 5/5 queries true; no executable V2V campaign | Partially supported | “The V2V model satisfies its recorded symbolic queries.” |
| Handover token is bound, short-lived, one-time, replay-resistant | `results/raw/proverif/handover_token.out.txt` | Symbolic token queries | 4/4 true; no dedicated replay attack CSV | Partially supported | “The model verifies the recorded token-binding conditions; dedicated replay measurements are absent.” |
| Invalid/expired token triggers fallback | No validating result file; implementation path only | Fallback events | `fallback_used=0` in the only pilot; invalid-token trials NOT FOUND | Partially supported | “A fallback path exists, but invalid/expired-token behavior was not experimentally validated.” |
| Reputation PBFT reduces consensus latency | `results/summary/pbft_validation_summary.csv` | Mean latency, 20 seeds/scenario | 4.803471 ms vs 5.458490 ms; 12.0% lower in development model | Partially supported | “The 20-seed rule-based model reports 12.0% lower latency; packet-level validation is required.” |
| Reputation PBFT detects malicious nodes | `results/raw/pbft_validation.csv`; summary | Detection rate | Mean 1.0 in modeled quarantined/revoked/honest-then-malicious scenarios | Partially supported | “The development model detected its modeled malicious scenarios with rate 1.0.” |
| Reputation PBFT avoids excessive temporary-fault penalties | PBFT raw/summary CSVs | Detection/removal in temporary-fault scenario | Detection=0.0; quarantine/revocation not reached across 20 seeds | Partially supported | “No temporary-fault node was removed in the development scenario.” |
| ProVerif verifies session-key secrecy | `results/raw/proverif/verification_table.csv` and raw outputs | Symbolic secrecy queries | V2R 4/4, handover 4/4, V2V 5/5 true | Fully supported (symbolic scope) | “All recorded secrecy queries returned true under the stated symbolic assumptions.” |
| ProVerif verifies mutual authentication | ProVerif raw outputs/table | Correspondence queries | Recorded authentication queries true | Fully supported (symbolic scope) | “The recorded authentication correspondences returned true.” |
| ProVerif verifies replay resistance | No dedicated replay-query artifact | Replay query | NOT FOUND | Unsupported | “Freshness checks address replay at the protocol level; no dedicated ProVerif replay query is reported.” |
| ProVerif verifies handover-token authenticity/destination binding | `results/raw/proverif/handover_token.out.txt` | Token correspondence | 4/4 true | Partially supported (symbolic scope) | “The handover model returned true for its recorded token-authentication and binding conditions.” |
| ProVerif verifies V2V message integrity | `results/raw/proverif/v2v_session.out.txt` | Integrity correspondence | 5/5 true | Fully supported (symbolic scope) | “The V2V model returned true for all five recorded queries, including integrity.” |
| OMNeT++/Veins/SUMO campaign measures latency, overhead, PDR, throughput, success | `results/raw/handover_results.csv` | Campaign metrics | Only one pilot row with latency/success; overhead/PDR/throughput and 20 seeds NOT FOUND | Unsupported as complete campaign | “Only a one-run latency/success pilot is available.” |
| liboqs benchmark measures ML-KEM/ML-DSA costs | `results/raw/crypto_benchmark.csv` | Mean/median/stddev/95% CI half-width | Six operations, 1,000 repetitions each, success count 1,000 | Fully supported for benchmark scope | “The standalone benchmark measured six ML-KEM-768/ML-DSA-65 operations over 1,000 repetitions each.” |

## Evidence classification

### OMNeT++/Veins/SUMO measured results

`results/raw/handover_results.csv` is a one-run native pilot. It supports only the scoped latency comparison and handover-success observation. It does not support campaign-wide density, speed, spacing, PDR, throughput, overhead, or confidence claims.

### liboqs benchmark results

`results/raw/crypto_benchmark.csv` is a standalone native benchmark with 1,000 repetitions per operation and timing dispersion. The CSV does not include hardware or exact liboqs version metadata.

### ProVerif symbolic results

The three raw outputs and `verification_table.csv` report true symbolic queries. These are model-level results under Dolev–Yao/ideal-primitive and freshness/channel assumptions, not empirical performance or computational-security proofs.

### Development-model results

`results/raw/pbft_validation.csv` and `results/summary/pbft_validation_summary.csv` provide 20-seed rule-based PBFT comparisons. They are useful for checking the development logic and scenario bookkeeping, but they are not packet-level network measurements.

### Assumptions

- Registered keys, idealized ML-KEM/ML-DSA primitives, secure randomness, and modeled freshness/channel conditions for ProVerif.
- Seeded development latency model for PBFT.
- Existing two-RSU OMNeT++ topology for the pilot.

### Unsupported claims

No claim of a complete multi-RSU campaign, real-CAV validation, statistical significance, dedicated replay/fallback attack validation, executable V2V performance, or computational security should be made from the current evidence.

