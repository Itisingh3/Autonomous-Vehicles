# Research Understanding Report

**Evidence rule.** This report is derived from repository files, CSV headers/values, plots, protocol documents, simulation configuration, and ProVerif source. Any value not found in those artifacts is marked **NOT FOUND**. The report does not treat a development stochastic model as an OMNeT++/Veins measurement.

## Relevant repository evidence

| Area | Relevant files |
|---|---|
| Architecture and protocol design | `docs/phases/Phase01_System_Model.md` through `Phase08_Reputation_Based_PBFT.md`, `docs/protocol/reputation_pbft_protocol.md`, `docs/diagrams/System_Model.md` |
| Cryptography | `crypto/PqcCrypto.h`, `crypto/PqcCrypto.cc`, `crypto/mlkem_backend.py`, `crypto/mldsa_backend.py`, `crypto/benchmark.py` |
| CAV/RSU simulation | `simulation/omnetpp/CAVApp.cc`, `RSUApp.cc`, `CavMsg.msg`, `cav-pqc-network.ned`, `omnetpp.ini`, `simulation/sumo/config-static.xml` |
| PBFT/reputation | `experiments/reputation_model.py`, `experiments/run_reputation_sensitivity.py`, `configs/reputation_pbft.ini`, `simulation/pbft/pbft_reputation.cpp` |
| Experiments and artifacts | `experiments/run_final_experiments.py`, `experiments/create_publication_artifacts.py`, `results/raw/*`, `results/summary.md`, `paper/figures/*`, `paper/tables/*` |
| Formal verification | `proverif/v2r_handshake.pv`, `proverif/handover_token.pv`, `proverif/v2v_session.pv` |

## Elevator pitch

The project studies a connected-autonomous-vehicle security architecture that uses ML-KEM for session-key establishment and ML-DSA for authentication and integrity. A serving RSU predicts the next RSU and sends a short-lived, destination-bound signed handover token, allowing re-authentication with a fresh session key instead of repeating the complete exchange. V2V sessions use the same post-quantum primitives, while reputation-aware PBFT separates trust management from the safety path. Three ProVerif models check symbolic secrecy and authentication correspondences. The repository demonstrates the design and produces development evidence, but the final CSV sweep is explicitly a stochastic protocol model and not a completed instrumented OMNeT++/Veins campaign.

## Research problem and proposed solution

Vehicles exchange safety and control information frequently while moving between RSU coverage areas. Classical public-key mechanisms are threatened by quantum algorithms, and repeating a complete ML-KEM/ML-DSA exchange at every RSU adds cryptographic work and delay. The proposed solution is a mobility-aware handover: the current RSU predicts a destination, derives a context from the current session, signs a short-lived token, and transfers encrypted context over an RSU channel. The destination checks the token, pseudonym, freshness, destination binding, and a fresh vehicle signature, then derives a new session key. Invalid tokens fall back to the full V2R procedure.

## End-to-end lifecycle

1. **Registration:** the design documents assign the TA responsibility for device validation, pseudonyms, certificates, public keys, revocation, and traceability. A runnable registration implementation is **NOT FOUND**.
2. **V2R authenticated key establishment:** a vehicle sends a signed hello and ML-KEM public key; the RSU returns a signed ciphertext and nonce; the vehicle derives a key and sends key confirmation.
3. **Protected session:** AEAD is documented for application data; a complete executable application-data path is **PARTIALLY FOUND**.
4. **Handover:** the serving RSU predicts the next RSU, signs a token, transfers encrypted context, and the vehicle presents a fresh signed request to the next RSU.
5. **V2V:** the protocol document and ProVerif model specify direct and RSU-assisted V2V. A complete OMNeT++ V2V application is **NOT FOUND**.
6. **Trust management:** the reputation model uses a recent score for grouping and lifecycle decisions, a slower long-term score for audit and tie-breaking, severity events, a sliding window, quarantine, and distributed revocation.
7. **Formal analysis:** three symbolic models test secrecy and injective correspondences under stated ideal-primitive assumptions.

## Main contribution assessment

The strongest contribution is the explicit mobility-aware handover-token design and its fallback path. The second is the separation of cryptographic authority from reliability evidence: a failed signature, credential, freshness, or ciphertext check cannot be overridden by reputation or ML. The weakest contribution is the quantitative network-performance claim, because the broad sweep is marked `development_stochastic_protocol_model`, while the repository does not contain a completed multi-seed OMNeT++/Veins campaign.

## What is actually supported

| Claim | Evidence status |
|---|---|
| ML-KEM/ML-DSA V2R design exists | Implemented in C++ application code and modeled symbolically; repeated network evidence **NOT FOUND** |
| Handover is faster in the recorded development run | One CSV row: 18.3517 ms full versus 5.03833 ms handover, 72.55% reduction; no CI |
| Symbolic secrecy/authentication correspondences hold | V2R 4/4, handover 4/4, V2V 5/5 according to `paper/tables/table8_proverif_results.md` |
| Reputation sensitivity matrix exists | 48,600 raw rows, 2,430 grouped rows, 243 configurations, 20 seeds per case |
| Final factorial network campaign has 20–30 seeds | **NOT SUPPORTED**: `final_experiment_results.csv` has 4,320 rows, 2 seeds per 2,160 configurations |
| Real CAV trace or validated Veins campaign | **NOT FOUND** |

## Recommended networking-letter framing

Use the handover mechanism as the central systems contribution, describe the cryptographic benchmarks and broad sweep as development/simulation evidence, and state the ProVerif results only under their symbolic assumptions. Do not present stochastic values as measured vehicle-network performance. Remove or soften any statement that implies completed real-trace validation, statistically paired OMNeT++/Veins evidence, or implementation-level proof from ProVerif.

## Final assessment

- **Fully supported:** protocol equations and message intent in design/code; symbolic query outcomes as recorded; existence of reproducible CSV/plot generation.
- **Partially supported:** one-run handover improvement; one-run PBFT comparison; stochastic trends for throughput, PDR, cryptographic times, and detection.
- **NOT FOUND:** actual CAV traces, completed V2V network measurements, full registration executable, p-values/effect sizes, 20–30 seeds for the final factorial sweep, and formal proofs of computational security or implementation correctness.

## Suggested title options

1. *Mobility-Aware Post-Quantum Handover Authentication for Connected Autonomous Vehicles*
2. *Short-Lived Post-Quantum Handover Tokens for Secure CAV V2R Communication*
3. *Authenticated ML-KEM Session Handover for Secure Connected Vehicles*

## Suggested contribution list

1. A mobility-aware ML-DSA-signed, destination-bound handover-token protocol with full-exchange fallback.
2. An ML-KEM/ML-DSA authenticated V2R and V2V protocol specification with transcript and freshness binding.
3. An explainable sliding-window reputation mechanism integrated with PBFT lifecycle decisions.
4. Symbolic verification and reproducible development evaluation, with explicit limits on network-level evidence.
