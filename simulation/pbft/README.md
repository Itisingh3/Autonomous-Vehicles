# Reputation-based PBFT experiment

This standalone experiment is intentionally separate from the V2R and RSU
handover applications. It uses 13 consensus nodes (`f=4`, quorum `2f+1=9`),
initial reputation 100, and the update rule `clip(R + alpha*valid - beta*invalid
- gamma*missed, 0, 100)` with `alpha=1`, `beta=5`, and `gamma=2`.

Every Request, Pre-Prepare, Prepare, Response, and Reply is signed and verified
with ML-DSA-65. The adaptive run applies dynamic eligibility, low-threshold
quarantine, and revocation after 2f+1 confirmation. The output compares it with
standard PBFT and is written to `results/raw/pbft_results.csv`.
