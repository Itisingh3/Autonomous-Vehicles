# Minimum validation execution log

Date: 2026-10-18

## Status

| Step | Status | Evidence |
|---|---|---|
| Linux OMNeT++ build/campaign | BUILD/PILOT COMPLETED; MINIMUM CAMPAIGN BLOCKED | Native WSL build succeeded and a deterministic pilot completed. The acceptance gate reports only one handover transition because the current application topology has two RSUs; the required 3–5-RSU campaign is therefore not claimed. |
| SUMO validation | COMPLETED in native WSL | `simulation/sumo/validation.sumocfg` completed with seed 42. |
| Standalone liboqs benchmark | COMPLETED in native WSL | Six operations, 1,000 repetitions each, with ML-KEM-768 and ML-DSA-65; copied to `results/raw/crypto_benchmark.csv`. |
| ProVerif | COMPLETED | All three Windows ProVerif 2.05 commands exited with status 0; complete outputs are under `results/raw/proverif/`. |
| PBFT validation | COMPLETED as rule-based development validation | 240 paired rows (20 seeds × 6 scenarios × 2 modes) in `results/raw/pbft_validation.csv`. |
| Unit-test suite | BLOCKED in current checkout | Python package directories imported by the existing tests (`protocol`, `consensus`, `ml`, `sim`, `data`) are absent from this checkout. |

## ProVerif outputs

- `results/raw/proverif/v2r_handshake.out.txt`
- `results/raw/proverif/handover_token.out.txt`
- `results/raw/proverif/v2v_session.out.txt`
- `results/raw/proverif/verification_table.csv`

## PBFT outputs

- `results/raw/pbft_validation.csv`
- `results/summary/pbft_validation_summary.csv`

These PBFT outputs are not network-simulator measurements and must not be merged into the final evidence summary until the required 3–5-RSU OMNeT++/Veins/SUMO campaign passes. The independent crypto benchmark has completed successfully.
