# Reputation-based PBFT protocol

Each node starts with `R_recent=R_long=100`. Every consensus round records a bounded event window of size `W`, containing event type, severity, timestamp, node ID, evidence hash, and round number. Valid contributions earn `alpha`; missed required messages incur `gamma`; invalid events use configurable severity penalties and the recent-score forgiveness rule.

PBFT phases remain signed REQUEST, PRE-PREPARE, PREPARE, RESPONSE, and REPLY. ML-DSA signs control messages; ML-KEM is not used for signatures. Recent reputation controls eligibility, quarantine, and revocation. Long-term reputation is used for auditing, tie-breaking, leader preference, and recovery.

The leader uses the existing view rule `p=v mod CN`, with optional `argmax(R_recent + epsilon*u)`. Membership changes occur every configurable reassignment interval and never reduce the active set below `3f+1`.
