# CAV PQC framework: implementation plan

This repository retains its working modules (`protocol/`, `crypto/`,
`consensus/`, `ml/`, and `sim/`) and adds this phase structure as the
implementation record.  The phase documents define acceptance criteria before
any result is used in the networking letter.

| Phase | Scope | Primary implementation |
|---|---|---|
| 00 | reproducible environment | `docs/phases/Phase00_Environment.md` |
| 01 | system model | `docs/phases/Phase01_System_Model.md` |
| 02 | threat model | `docs/phases/Phase02_Threat_Model.md` |
| 03 | ML-KEM/ML-DSA service | `crypto/`, `sim/omnet/src/crypto/` |
| 04 | TA registration | `protocol/registration.py` |
| 05 | initial V2R AKE | `protocol/ake.py` |
| 06 | handover | `sim/omnet/src/protocol/` |
| 07 | V2V | pending Veins application module |
| 08 | reputation/PBFT | `consensus/` |

Development-model output is never labelled as SUMO/Veins/OMNeT++ evidence.
