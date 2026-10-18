# ProVerif Concepts

## What the models mean

ProVerif is a symbolic protocol verifier. A Dolev–Yao attacker controls the public channel and can intercept, replay, compose, and modify messages, but cannot break the idealized cryptographic equations or protected private channels. This is different from computational security: ProVerif does not measure concrete ML-KEM/ML-DSA hardness, implementation timing, side channels, or random-number quality.

## Model inventory

| File | Entities and abstraction | Events/queries | Recorded outcome |
|---|---|---|---|
| `proverif/v2r_handshake.pv` | Vehicle, RSU, public channel; ideal `encaps/decaps`, `sign/foobar`, transcript and Finished functions | `attacker(secret_probe)` plus three injective correspondences for hello/verification/session | 4/4 true according to `table8_proverif_results.md` |
| `proverif/handover_token.pv` | Current RSU, vehicle, next RSU, protected `rsu_channel`; token, context AEAD, fresh nonces | secrecy probe and three injective token/vehicle/session correspondences | 4/4 true |
| `proverif/v2v_session.pv` | Initiator, responder, public channel; ideal KEM, signatures, AEAD | secrecy probe plus hello, mutual verification, session, integrity correspondences | 5/5 true |

## Query interpretation

`attacker(secret_probe)` is a secrecy sanity query using a private probe. Injective event correspondence means every accepted event has a unique matching prior event, which models authentication/freshness under the symbolic abstraction. The models do not query real certificate parsing, clock arithmetic, nonce-cache state, PBFT quorum, revocation ledger, or implementation memory erasure.

## How to run

```powershell
proverif proverif\v2r_handshake.pv
proverif proverif\handover_token.pv
proverif proverif\v2v_session.pv
```

The repository documents expected successful secrecy/authentication/integrity results. A captured machine-readable ProVerif output file is **NOT FOUND**; `paper/tables/table8_proverif_results.md` is the recorded summary.

## Security scope

The models support symbolic claims about secrecy, correspondence authentication, token binding, and message integrity under ideal primitives and registered-key assumptions. They do not prove computational security, concrete PQ security levels, performance, denial-of-service resilience, conditional traceability, PBFT safety/liveness, or correctness of the C++ implementation. Observational equivalence is **NOT FOUND** in the repository.
