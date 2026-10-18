# PBFT and Reputation Concepts

## PBFT in this project

PBFT tolerates Byzantine replicas when `CN >= 3f + 1`; with `f=4`, the recorded development run uses 13 nodes and a quorum of `2f+1=9`. A leader receives a signed request, broadcasts Pre-Prepare, replicas exchange Prepare evidence, collect commit/response evidence, and return Reply after quorum. ML-DSA signatures are required by the design for client, leader, and replica control messages. The C++ artifact records phase counters; a full network message exchange is not independently evidenced.

## Reputation equations

| Formula | Meaning/example | Status |
|---|---|---|
| `R_i(0)=100` | Both recent and long-term scores begin at 100. | Explicitly implemented in `experiments/reputation_model.py`. |
| `delta_i=alpha*g_i-sum(beta(s_i,k))-gamma*n_i` | With `alpha=1`, one valid contribution and one medium missed message penalty 2, `gamma=2`, delta is `1-2-2=-3`. | Implemented; event representation is in Python. |
| `R_recent(t+1)=clip((1-lambda_recent)R_recent(t)+delta,0,100)` | At 100, lambda=.10 and delta=-3: 87. | Implemented. |
| `R_long(t+1)=clip((1-lambda_long)R_long(t)+delta,0,100)` | At 100, lambda=.01 and delta=-3: 96. | Implemented. |
| `A=valid_last_W/evaluated_last_W` | One valid and one medium fault gives accuracy .5. | Implemented. |
| `beta_eff=beta(s)(1-rho A)` | For medium beta=2, rho=.5, A=.5: 1.5. High/critical events are not forgiven. | Implemented, with event-type exclusions. |
| `T_low=mu-sigma; T_high=mu+sigma` | Mean and standard deviation of recent scores create dynamic grouping bands. | Implemented. |
| `CN>=3f+1; Q=2f+1` | For f=4, CN>=13 and Q=9. | Configured and used in the development model; full distributed enforcement is partial. |
| `M_i=sum omega(severity)` | Low=.2, medium=.5, high=1, critical=2 over the last W events. | Implemented. |
| `M<w thresholds` | theta1=1, theta2=2, theta3=4 classify trusted/suspicious/quarantined; critical evidence can revoke. | Implemented with the caveat that quarantined/revoked semantics should be audited against the protocol document. |

## Severity policy

| Event | Severity | Default penalty |
|---|---|---:|
| delayed eventually-valid / optional miss | Low | -1 |
| required miss | Medium | -2 |
| invalid timestamp/nonce | Medium | -3 in the documented table; the Python default medium penalty is 2, so this distinction is **INCONSISTENT** |
| conflicting PREPARE/COMMIT | High | -5 |
| invalid ML-DSA, Sybil, confirmed position falsification | Critical | -15 |
| confirmed collusion | Critical | -20 |

The Python model uses configurable `beta_low=1`, `beta_medium=2`, `beta_high`, `beta_critical=15`, and `beta_collusion=20`. It does not provide a separate default of 3 for invalid timestamp/nonce; this is a documented inconsistency.

## Fairness and exploitation resistance

Low/medium forgiveness reduces the penalty when recent accuracy is high, so one temporary fault does not erase a long record. High/critical events bypass forgiveness. The sliding window limits stale evidence and prevents an old honest history from indefinitely hiding new malicious behavior. Recent reputation drives eligibility and quarantine; long-term reputation is retained for historical audit and recovery/tie-breaking. A full leader preference implementation with epsilon randomization is **NOT FOUND**.

## Results

The one-run PBFT CSV reports standard latency 36.3343 ms and reputation latency 31.0289 ms, with 13 nodes, f=4, quorum=9, 10 eligible nodes, 3 quarantined, and 3 revoked in the adaptive row. The sensitivity matrix contains 48,600 rows across 243 parameter combinations, 10 scenarios, and 20 seeds. It is a Python rule-based development experiment, not an OMNeT++ consensus campaign. The C++ source currently acts as an integration smoke/output writer rather than a complete implementation of every sliding-window rule; this limits claims about deployed PBFT behavior.
