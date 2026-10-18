# Final Evidence-to-Claim Audit

This audit uses only result files currently present in the repository. It does not treat documented equations or code paths as measured evidence. “Fully supported” means the requested claim is directly evidenced at the stated scope; “partially supported” means evidence exists but is limited by scope, model fidelity, or missing negative/replicated tests; “unsupported” means the required evidence is absent.

## Evidence classes

- **OMNeT++/Veins/SUMO measured:** `results/raw/handover_results.csv` is a one-run native pilot. It uses the existing two-RSU topology, so it is not the requested multi-RSU campaign.
- **liboqs measured:** `results/raw/crypto_benchmark.csv` contains six native liboqs operations, each with 1,000 repetitions and timing statistics.
- **ProVerif symbolic:** `results/raw/proverif/verification_table.csv` and the three raw output files contain successful symbolic query results under the model assumptions.
- **Development model:** `results/raw/pbft_validation.csv` and `results/summary/pbft_validation_summary.csv` contain a 20-seed, rule-based PBFT comparison; this is not packet-level OMNeT++/Veins/SUMO evidence.
- **Not current validation evidence:** older factorial/development CSVs and older publication tables must not be substituted for the files identified above.

## Claim-by-claim audit

### 1. Handover-token authentication reduces re-authentication latency

- **Supporting experiment:** native OMNeT++ pilot, one full V2R run and one handover transition.
- **Result file:** `results/raw/handover_results.csv`.
- **Figure/table:** current-run publication figure/table: **NOT FOUND**. Existing older table artifacts are stale relative to this CSV.
- **Metric:** full latency = 18.3647 ms; handover latency = 5.03833 ms; success = 1.
- **Seeds/repetitions:** 1 run; no confidence interval.
- **Baseline:** full V2R handshake in the same run.
- **Improvement:** `(18.3647-5.03833)/18.3647 = 72.5651%` for this run only.
- **Support:** **Partially supported**. The result is a pilot, not a replicated 3–5-RSU campaign.
- **Safe wording:** “In a single native OMNeT++ pilot run, handover-token authentication completed in 5.03833 ms versus 18.3647 ms for the full exchange, a 72.5651% reduction; replicated multi-RSU evaluation remains outstanding.”

### 2. V2R establishes matching session keys

- **Supporting experiment:** V2R implementation pilot and symbolic V2R model.
- **Result files:** `results/raw/handover_results.csv`; `results/raw/proverif/v2r_handshake.out.txt`.
- **Figure/table:** `results/raw/proverif/verification_table.csv`; no explicit key-equality publication figure.
- **Metric:** successful handshake (`handover_success=1`); symbolic query summary 4/4 true.
- **Seeds/repetitions:** 1 executable pilot; symbolic model, not statistical repetitions.
- **Baseline:** none.
- **Improvement:** NOT APPLICABLE.
- **Support:** **Partially supported**; the CSV does not log both derived key values or an equality assertion.
- **Safe wording:** “The pilot completed a successful V2R exchange, and the symbolic model verifies the modeled session-key correspondence under its assumptions.”

### 3. V2V establishes secure vehicle-to-vehicle session keys

- **Supporting experiment:** ProVerif V2V model.
- **Result file:** `results/raw/proverif/v2v_session.out.txt`.
- **Figure/table:** `results/raw/proverif/verification_table.csv` (5/5 true).
- **Metric:** symbolic secrecy/authentication/integrity queries.
- **Seeds/repetitions:** symbolic analysis; no executable V2V campaign found.
- **Baseline:** none.
- **Improvement:** NOT APPLICABLE.
- **Support:** **Partially supported** (symbolic only).
- **Safe wording:** “The V2V model satisfies its five recorded ProVerif queries under symbolic assumptions; an executable V2V performance validation is not present.”

### 4. Token is destination-bound, short-lived, one-time, and replay-resistant

- **Supporting experiment:** handover implementation and symbolic handover model.
- **Result files:** `results/raw/proverif/handover_token.out.txt`; implementation source; no negative-attack CSV.
- **Figure/table:** `results/raw/proverif/verification_table.csv` (4/4 true).
- **Metric:** symbolic token-authentication queries; implementation checks for destination, expiry, nonce/use state.
- **Seeds/repetitions:** symbolic analysis; no replay test repetitions recorded.
- **Baseline:** full V2R fallback is the design fallback, not a measured comparator here.
- **Improvement:** NOT APPLICABLE.
- **Support:** **Partially supported**; replay resistance is not isolated by a dedicated empirical attack result.
- **Safe wording:** “The design and symbolic handover model bind the token to its destination and freshness fields; dedicated replay-attack measurements are not reported.”

### 5. Invalid or expired tokens trigger fallback

- **Supporting experiment:** implementation path includes fallback logic.
- **Result file:** no result file recording invalid/expired-token trials; `results/raw/handover_results.csv` records only `fallback_used=0`.
- **Figure/table:** NOT FOUND.
- **Metric:** fallback event count is not exercised in the available result.
- **Seeds/repetitions:** 0 invalid/expired test runs found.
- **Baseline:** full V2R handshake.
- **Improvement:** NOT APPLICABLE.
- **Support:** **Partially supported** as an implementation feature, unsupported as an experimental result.
- **Safe wording:** “The implementation contains a full-authentication fallback path; its behavior under invalid or expired tokens was not experimentally validated in the available results.”

### 6. Reputation PBFT reduces consensus latency versus standard PBFT

- **Supporting experiment:** 20-seed rule-based development comparison across six scenarios.
- **Result files:** `results/raw/pbft_validation.csv`; `results/summary/pbft_validation_summary.csv`.
- **Figure/table:** current publication artifact: NOT FOUND.
- **Metric:** mean consensus latency: standard 5.458490 ms (95% CI half-width 0.135423), reputation 4.803471 ms (0.119172).
- **Seeds/repetitions:** 20 seeds per mode/scenario.
- **Baseline:** standard PBFT.
- **Improvement:** 12.0000% for the development model’s paired means.
- **Support:** **Partially supported**; the model is not a network simulation and the same latency scaling appears across scenarios.
- **Safe wording:** “In the 20-seed rule-based development model, reputation PBFT had 4.803471 ms mean consensus latency versus 5.458490 ms for standard PBFT (12.0% lower); packet-level network validation is still required.”

### 7. Reputation PBFT detects malicious nodes

- **Supporting experiment:** development PBFT scenarios (`quarantined`, `revoked`, `honest_then_malicious`).
- **Result files:** PBFT raw and summary CSVs.
- **Figure/table:** NOT FOUND for a current publication artifact.
- **Metric:** detection rate mean = 1.0 in those modeled scenarios; 0.0 in honest/suspicious/temporary-fault scenarios.
- **Seeds/repetitions:** 20 per scenario/mode.
- **Baseline:** standard PBFT rows are included, but standard PBFT is not a detector implementation.
- **Improvement:** NOT CALCULATED; no detector baseline comparison is defined.
- **Support:** **Partially supported** (development model only).
- **Safe wording:** “The rule-based development scenarios detected the modeled malicious states with a mean detection rate of 1.0; this is not evidence of real-network attack-detection performance.”

### 8. Reputation PBFT avoids excessive penalties for temporary faults

- **Supporting experiment:** `temporary_fault` development scenario and reputation design.
- **Result files:** PBFT raw/summary CSVs.
- **Figure/table:** NOT FOUND.
- **Metric:** temporary-fault rows show detection rate 0.0 and no quarantine/revocation (`-1` means not reached).
- **Seeds/repetitions:** 20 per mode.
- **Baseline:** standard PBFT temporary-fault rows.
- **Improvement:** NOT CALCULATED; no reputation trajectory or penalty magnitude is exported in the summary.
- **Support:** **Partially supported**.
- **Safe wording:** “In the development temporary-fault scenario, no node was detected or removed across 20 seeds; the exported results do not establish fairness under packet-level faults.”

### 9. ProVerif verifies session-key secrecy

- **Supporting experiment:** all three ProVerif models.
- **Result files:** three raw outputs and `verification_table.csv`.
- **Figure/table:** `results/raw/proverif/verification_table.csv`: V2R 4/4, handover 4/4, V2V 5/5 true.
- **Metric:** symbolic secrecy queries.
- **Seeds/repetitions:** one symbolic analysis per model.
- **Baseline:** none.
- **Improvement:** NOT APPLICABLE.
- **Support:** **Fully supported at the symbolic-model scope**.
- **Safe wording:** “ProVerif returned true for all recorded secrecy queries in the V2R, handover, and V2V models under their stated symbolic assumptions.”

### 10. ProVerif verifies mutual authentication

- **Supporting experiment:** correspondence events in the three ProVerif models.
- **Result files:** raw ProVerif outputs and verification table.
- **Figure/table:** verification table, with query details in raw outputs.
- **Metric:** authentication correspondence queries, all recorded true.
- **Seeds/repetitions:** one symbolic analysis per model.
- **Baseline/improvement:** NOT APPLICABLE.
- **Support:** **Fully supported at symbolic scope**.
- **Safe wording:** “The recorded ProVerif correspondence queries for modeled authentication events returned true.”

### 11. ProVerif verifies replay resistance

- **Supporting experiment:** freshness checks are modeled or assumed, but no dedicated replay query is recorded.
- **Result file:** ProVerif outputs; no replay-specific result artifact.
- **Figure/table:** NOT FOUND.
- **Metric:** NOT FOUND.
- **Seeds/repetitions:** NOT APPLICABLE.
- **Baseline/improvement:** NOT APPLICABLE.
- **Support:** **Unsupported as stated**.
- **Safe wording:** “Replay resistance is addressed by protocol freshness fields and executable checks; a dedicated ProVerif replay query is not reported.”

### 12. ProVerif verifies handover-token authenticity and destination binding

- **Supporting experiment:** handover-token model.
- **Result file:** `results/raw/proverif/handover_token.out.txt`.
- **Figure/table:** verification table, 4/4 true.
- **Metric:** symbolic token-authentication/correspondence queries.
- **Seeds/repetitions:** one symbolic analysis.
- **Baseline/improvement:** NOT APPLICABLE.
- **Support:** **Partially supported**; symbolic binding is modeled, but no executable attack campaign exists.
- **Safe wording:** “The handover-token model returned true for its four recorded queries, including modeled origin and destination-binding conditions.”

### 13. ProVerif verifies V2V message integrity

- **Supporting experiment:** V2V ProVerif model.
- **Result file:** `results/raw/proverif/v2v_session.out.txt`.
- **Figure/table:** verification table, 5/5 true.
- **Metric:** symbolic integrity/authentication correspondence queries.
- **Seeds/repetitions:** one symbolic analysis.
- **Baseline/improvement:** NOT APPLICABLE.
- **Support:** **Fully supported at symbolic scope**.
- **Safe wording:** “The V2V symbolic model returned true for all five recorded queries, including its modeled message-integrity correspondence.”

### 14. OMNeT++/Veins/SUMO campaign measures latency, overhead, PDR, throughput, and handover success

- **Supporting experiment:** only a native OMNeT++ pilot and SUMO validation run exist.
- **Result file:** `results/raw/handover_results.csv` contains latency and success only.
- **Figure/table:** campaign CSV/plot for the requested multi-RSU experiment: NOT FOUND.
- **Metric:** full latency, handover latency, success, fallback flag; no overhead/PDR/throughput columns.
- **Seeds/repetitions:** 1 pilot run; not 20 seeds.
- **Baseline/improvement:** full V2R is the latency baseline; no valid campaign-wide percentage.
- **Support:** **Unsupported as a complete campaign claim**.
- **Safe wording:** “A one-run OMNeT++ pilot measured latency and handover success; the planned multi-RSU campaign with overhead, PDR, throughput, and 20 seeds is not available.”

### 15. liboqs benchmark measures ML-KEM and ML-DSA operation costs

- **Supporting experiment:** standalone native liboqs benchmark.
- **Result file:** `results/raw/crypto_benchmark.csv`.
- **Figure/table:** current publication artifact: NOT FOUND; the CSV is the authoritative result.
- **Metric:** mean, median, standard deviation, and 95% CI half-width for key generation, encapsulation, decapsulation, signing, and verification.
- **Seeds/repetitions:** 1,000 repetitions per operation; all success counts = 1,000.
- **Baseline:** none.
- **Improvement:** NOT APPLICABLE.
- **Support:** **Fully supported for the measured benchmark scope**; hardware and library-version metadata are absent from the CSV.
- **Safe wording:** “The standalone liboqs benchmark completed 1,000 successful repetitions for each ML-KEM-768 and ML-DSA-65 operation and reports timing dispersion and 95% confidence half-widths.”

## Assumptions and evidence limitations

1. ProVerif treats cryptographic primitives symbolically and assumes registered/bound keys, secure randomness, and the modeled channel/freshness conditions. It does not prove computational security, implementation correctness, side-channel resistance, or PBFT liveness.
2. The PBFT CSV is a deterministic/rule-based development model with seeded latency generation, not OMNeT++/Veins/SUMO packet-level evidence.
3. The OMNeT++ pilot has two RSUs and one transition; it is not the requested 3–5-RSU, 20-seed campaign.
4. The liboqs CSV lacks CPU, operating-system, liboqs commit/version, and compiler metadata.
5. No p-values or between-seed statistical tests are present. Confidence intervals are reported only where the source CSV provides them.

## Claims that must remain unsupported

- Generalized network-performance claims for throughput, packet-delivery ratio, message overhead, or handover success over density/speed grids.
- Statistical significance of the handover reduction.
- Real-CAV trace validation.
- Dedicated empirical replay/fallback attack results.
- Computational or implementation-level security guarantees from ProVerif.
- Executable V2V performance or key-equality measurements.

