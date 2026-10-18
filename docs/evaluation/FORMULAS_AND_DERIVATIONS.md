# Formulas and Derivations

## Cryptographic formulas

| Formula | Purpose/source/status | Example |
|---|---|---|
| `(ek,dk)=KeyGen()` | ML-KEM key generation; protocol docs and wrappers; implemented/modelled. | **NOT NUMERIC**: keys are byte strings. |
| `(K,c)=Encaps(ek); K'=Decaps(dk,c)` | Shared-secret agreement; V2R/V2V; implemented/modelled. | Success requires `K'=K`; a current CSV equality log is **NOT FOUND**. |
| `H=Hash(m_1||m_2||...)` | Transcript binding; C++ and ProVerif. | Any changed field changes the transcript digest. |
| `K_s=KDF(K||H(ek||c||n_v||n_r||p_v||ID_r))` | V2R session derivation; documented and equivalent context used in C++. | The exact numeric key is **NOT FOUND**. |
| `delta=Sign(sk,H(m)); Verify(pk,H(m),delta)` | Authentication/integrity; C++ and ProVerif. | Invalid signature causes failure; no numeric signature is reported. |
| `C=AEAD.Encrypt(K,m,AD); m=Decrypt(K,C,AD)` | Confidentiality/integrity; context and V2V model. | Authentication-tag failure rejects; payload values **NOT FOUND**. |
| `K_ctx=KDF(K_i,a||"handover-context")` | Handover context separation; implemented. | Context hash is carried in the token; raw key **NOT FOUND**. |
| `HT=Sign(sk_a,H(p||b||H(K_ctx)||t_i||t_e||n_h))` | Token authenticity/binding; implemented. | `t_e=t_i+5 s` in the configured RSU path. |
| `K_i,b=KDF(K_ctx||n_v'||n_b||t)` | Fresh handover session; implemented/modelled. | Nonces are fresh byte strings; numeric key **NOT FOUND**. |

## Performance formulas

| Formula | Variables/status | Example/data |
|---|---|---|
| `L_end=L_crypto+L_network+L_queue` | End-to-end latency decomposition; conceptual, not directly logged as three terms. | Components **NOT FOUND** separately. |
| `L_avg=(1/N)sum L_i` | Mean latency; used by scripts/summary. | One-run handover mean equals its only observation: 18.3517 ms/full. |
| `Throughput=delivered_messages/time` | Messages/s; stochastic script. | Overall summary: 143.56 messages/s, development-model value. |
| `PDR=received/sent` | Packet delivery ratio; stochastic script. | Overall summary: .8768. |
| `Overhead=sum control/application bytes` | Communication overhead; stochastic script. | Overall summary: 1211.92 bytes. |
| `Reduction=100(L_full-L_token)/L_full` | Handover benefit. | One-run: 72.55%; broad model mean: 64.00%. |

## PBFT and reputation formulas

| Formula | Status/example |
|---|---|
| `CN>=3f+1` | PBFT safety condition; f=4 => CN>=13, recorded configuration uses 13. |
| `Q=2f+1` | Commit/revocation quorum; f=4 => Q=9; recorded PBFT CSV. |
| `f_max=floor((CN-1)/3)` | Derived maximum Byzantine count; for CN=13, f_max=4. Formula is documented, not separately logged. |
| `R_i(0)=100` | Implemented in Python model. |
| `delta=alpha*g-sum(beta)-gamma*n` | Implemented; event penalties configurable. |
| `R_recent'=clip((1-lambda_recent)R_recent+delta,0,100)` | Implemented; default lambda=.10. |
| `R_long'=clip((1-lambda_long)R_long+delta,0,100)` | Implemented; default lambda=.01. |
| `A=valid_last_W/evaluated_last_W` | Implemented with W=20 default. |
| `beta_eff=beta(1-rho A)` | Implemented for low/medium non-exempt events; rho=.5. |
| `M_i=sum_{last W}omega(severity)` | Implemented; weights .2/.5/1/2. |
| `T_low=mu-sigma; T_high=mu+sigma` | Implemented for grouping. |
| `Detection=TP/(TP+FN)` | Metric column exists, but attack confusion aggregation is model-generated; formula is standard and not separately documented in code. |
| `FPR=FP/(FP+TN)` | Metric column exists; underlying labels are scenario labels in the stochastic model. |
| `FNR=FN/(TP+FN)` | Metric column exists; no independent trace validation. |

## Missing derivations

Formal derivations for certificate issuance, conditional traceability, secure hardware, warm-up, channel capacity, and a measured latency confidence interval are **NOT FOUND**. The repository also does not contain a p-value or effect-size formula/application.
