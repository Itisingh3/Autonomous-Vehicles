# Repository structure

This is the maintained project layout.  The first group matches the CAV-PQC
research workspace; the second holds executable source retained at the root so
existing Python imports and reproducibility commands remain valid.

```text
autonomous-vehicles-using-post-quantum-cryptography/
├── README.md
├── docs/                         # plan, phase records, protocol/security notes
├── crypto/                       # Python providers and liboqs integration point
├── simulation/                   # canonical OMNeT++/SUMO/Veins integration roots
├── sim/omnet/                    # containerized C++ liboqs adapter
├── proverif/                     # compatibility entry point for formal work
├── formal/                       # executable ProVerif models
├── results/                      # final raw data and plots only
├── reports/                      # generated development/formal reports
├── paper/                        # networking-letter figures and tables
├── references/                   # source papers and bibliographic notes
├── data/                         # separated ROAD and CAV telemetry processing
├── protocol/ consensus/ ml/      # executable research implementation
├── analysis/ tests/ tools/       # experiment/report tooling and tests
├── configs/ notebooks/ spec/     # configuration and reproducibility material
└── artifacts/                    # portable Colab bundle/model artifacts
```

`reports/` remains separate from `results/`: reports include development-only
outputs and must not be copied into final networking-letter tables.  ROAD CAN
data stays separate from CAV reliability telemetry under `data/`.

The formal source of truth remains `formal/`; `proverif/` is reserved for a
future external ProVerif workspace and must not contain copied, divergent
models.
