# CAV system model and latency boundary

```text
CAV ── safety/V2V ── neighboring CAV
 │
 └── safety + authentication/V2R ── RSU ── MEC ── PBFT trust group ── TA/cloud
```

| Path | Messages | Required latency behaviour |
|---|---|---|
| Safety-critical | BSM/CAM, collision warning, cooperative maneuver | Deliver directly between CAVs or CAV and serving RSU; never wait for PBFT. |
| Session control | HELLO, CHALLENGE, FINISHED, handover token | Authenticate with ML-DSA and establish keys with ML-KEM. |
| Trust management | signed evidence, reputation update, PBFT messages, revocation | Edge/MEC path; asynchronous with respect to immediate safety actions. |
| Cloud/TA | credential issue, conditional traceability, archived analytics | Not on the real-time safety path. |

An RSU can accept the vehicle for safety traffic only after session acceptance.
A consensus decision may update eligibility or quarantine state for subsequent
traffic, but is not a prerequisite for an emergency warning.
