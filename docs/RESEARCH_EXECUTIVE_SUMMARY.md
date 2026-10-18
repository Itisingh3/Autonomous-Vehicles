# Executive Summary

## Project problem

Connected autonomous vehicles require frequent authenticated V2V and V2R communication while moving rapidly between roadside units. Conventional public-key mechanisms are vulnerable to quantum attacks, while repeatedly performing a complete post-quantum key establishment at every RSU can add latency and cryptographic processing. CAV trust management also requires Byzantine-tolerant consensus without placing blockchain/PBFT processing on the safety-critical communication path.

## Proposed solution

The repository specifies ML-KEM for session-key establishment, ML-DSA for authentication and integrity, transcript binding, fresh nonces, timestamps, and AEAD for protected data. A serving RSU predicts the next RSU, issues a short-lived destination-bound ML-DSA-signed handover token, transfers encrypted context, and enables the next RSU to derive a fresh session key; invalid tokens fall back to the complete V2R exchange. An explainable sliding-window reputation mechanism supports PBFT grouping, quarantine, and distributed revocation while keeping cryptographic validation authoritative.

## Main novelty

The central novelty is mobility-aware re-authentication using a short-lived, one-time, destination-bound handover token instead of repeating the full exchange at every RSU. The design combines this handover path with post-quantum V2R/V2V session establishment, symbolic verification, and explainable reputation-based PBFT lifecycle decisions.

## Main result

The recorded development handover run reports 18.3517 ms for the full V2R exchange and 5.03833 ms for token authentication, a 72.55% reduction in that single run. ProVerif result tables report all listed queries true for the V2R model (4/4), handover model (4/4), and V2V model (5/5), under their symbolic assumptions.

## Security properties verified

- Symbolic session-key secrecy probes.
- Injective authentication correspondences for V2R, handover, and V2V events.
- Handover-token origin, destination, freshness, and session-binding correspondences in the symbolic model.
- Message-integrity correspondence in the V2V model.
- Replay resistance is addressed by modelled fresh values and by implementation checks for timestamps, expiry, and one-time token nonces.

These are symbolic/model-level results. Computational security, implementation correctness, side-channel resistance, secure-hardware behavior, conditional traceability, and PBFT liveness are not established by the current evidence.

## Performance results

The one-run PBFT artifact reports 36.3343 ms for standard PBFT and 31.0289 ms for reputation-based PBFT, a 14.60% reduction. The broader factorial CSV is explicitly labelled `development_stochastic_protocol_model`; its recorded aggregate summary reports 4.2845 ms full latency, 1.5399 ms handover latency, 64.00% reduction, 0.8768 packet-delivery ratio, 143.56 messages/s throughput, and 12.12% lower reputation-based consensus latency. These values are development-model outputs, not validated OMNeT++/Veins network measurements.

## Limitations

- The final factorial experiment contains two seeds per configuration, not the 20–30 seeds described in older planning documents.
- A completed instrumented OMNeT++/Veins/SUMO campaign is **NOT FOUND**.
- Real CAV telemetry traces are **NOT FOUND**.
- Independent all-suite liboqs wall-clock benchmarks are **NOT FOUND**; the cryptographic CSV is a development aggregate.
- A complete executable registration service and complete V2V network experiment are **NOT FOUND**.
- P-values and effect sizes are **NOT FOUND**.
- The documented medium-severity timestamp/nonce penalty differs from the Python model default and requires reconciliation.

## Four networking-letter contributions

1. A mobility-aware ML-DSA-signed, destination-bound, short-lived handover-token protocol with full-exchange fallback.
2. An ML-KEM/ML-DSA authenticated key-establishment design for V2R and V2V communication with transcript and freshness binding.
3. An explainable sliding-window reputation mechanism separating recent and long-term reputation for PBFT grouping and malicious-node lifecycle decisions.
4. Symbolic verification and reproducible development evaluation with explicit evidence boundaries and limitations.

## Recommended title

**Mobility-Aware Post-Quantum Handover Authentication for Secure V2V and V2R Communication in Connected Autonomous Vehicles**

## Claims that must not be made

- Do not claim that the repository contains real-world CAV trace validation.
- Do not present the stochastic development CSV as an OMNeT++/Veins measurement campaign.
- Do not claim statistically reliable 20–30-seed factorial results.
- Do not claim that ProVerif proves computational security, implementation correctness, or concrete cryptographic timing.
- Do not claim complete executable registration, V2V network evaluation, PBFT liveness validation, or independent liboqs benchmarking unless new evidence is added.
