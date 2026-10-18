# Mobility-Aware Post-Quantum CAV Communication

This repository contains a development implementation of authenticated key establishment, mobility-aware RSU handover, V2V session modeling, reputation-based PBFT, and symbolic verification for connected autonomous vehicles.

## Current status

- ML-KEM and ML-DSA integration is implemented through the project crypto wrappers and liboqs-compatible APIs.
- OMNeT++/Veins application modules are under `simulation/omnetpp/`.
- The handover path records cryptographic wall-clock work separately from simulated latency and writes `results/raw/handover_results.csv` when the compatible simulator is built and run.
- Reputation-based PBFT development code is under `simulation/pbft/` and writes `results/raw/pbft_results.csv`.
- Symbolic models are under `proverif/`: V2R, RSU handover token, and V2V session establishment.
- The experiment sweep is implemented in `experiments/run_final_experiments.py`.
- The large sweep is explicitly a `development_stochastic_protocol_model`; it is not a substitute for instrumented CAV traces or a completed OMNeT++/Veins network campaign.

## Repository layout

`crypto/` contains crypto wrappers and benchmarks. `simulation/omnetpp/` contains the OMNeT++ CAV/RSU modules, while `simulation/pbft/` contains the PBFT development run. `simulation/veins/` contains Veins assets. `proverif/` contains the three symbolic models. `experiments/` contains reproducible sweep and publication-artifact scripts. Results are written to `results/raw/` and `results/plots/`; audit and reproducibility documentation is in `docs/evaluation/`; generated tables and figures are in `paper/tables/` and `paper/figures/`.

## Cryptographic design

- ML-KEM is used for key encapsulation and session-key establishment.
- ML-DSA is used for authentication, integrity, and non-repudiation.
- AEAD protects confidential application messages where configured.
- Transcript binding, fresh nonces, timestamps, key confirmation, pseudonym binding, and replay checks are part of the protocol design.
- Cryptographic failures remain authoritative and are not overridden by a learned reliability score.

## Locked toolchain

The target versions in `simulation/versions.lock` are OMNeT++ 6.1.0, Veins 5.3.1, SUMO 1.22.0, liboqs 0.12.0, and ProVerif 2.05. The older `simulation/omnetpp/README.md` documents a different `opp_env` combination; reconcile it with the lockfile before treating network output as final evidence.

## Python setup and tests

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
python -m py_compile experiments\run_final_experiments.py
python -m py_compile experiments\create_publication_artifacts.py
python -m pytest -q
```

Optional deep-learning dependencies are listed in `requirements-deep.txt`.

## Experiment sweep

```powershell
python experiments\run_final_experiments.py --smoke
python experiments\run_final_experiments.py --seeds 20
python experiments\run_final_experiments.py --seeds 30
```

The sweep covers speeds 30/50/80 km/h, densities 50–300, RSU spacing 250/400 m, three PQC suites, malicious rates 0/5/10/20%, and replay, forgery, Sybil, DoS, and false-position attacks. Seeds start at 42.

## Publication artifacts

```powershell
python experiments\create_publication_artifacts.py
```

This regenerates figures in `paper/figures/` and tables in `paper/tables/` from existing CSV results only.

## OMNeT++/Veins integration

Inside a compatible `opp_env` shell, after configuring liboqs and Veins paths:

```bash
cd simulation/omnetpp
opp_env run omnetpp-6.1.0 -c "make MODE=release -j2"
opp_env run omnetpp-6.1.0 -c "./cav_pqc_network -u Cmdenv -n .:../.neddeps -f omnetpp.ini"
```

The deterministic application run records V2R and handover metrics in `results/raw/handover_results.csv`. A compiled simulator is not included in the repository.

## PBFT development run

```bash
cd simulation/pbft
make MODE=release -j2
./pbft_reputation
```

The output is written to `results/raw/pbft_results.csv`.

## ProVerif verification

```powershell
& 'C:\Tools\proverif2.05\proverif.exe' proverif\v2r_handshake.pv
& 'C:\Tools\proverif2.05\proverif.exe' proverif\handover_token.pv
& 'C:\Tools\proverif2.05\proverif.exe' proverif\v2v_session.pv
```

The validated models report true secrecy/authentication/integrity correspondences under their documented symbolic assumptions.

## Evidence policy

Read `docs/evaluation/RESULT_AUDIT.md` before using any number in a paper. The audit distinguishes one-run measured development artifacts, stochastic simulated outputs, and formal-verification results. The current sweep must not be described as real CAV network evidence, and the existing one-run handover/PBFT CSVs do not provide confidence intervals. Reproduction details and known environment limitations are recorded in `docs/evaluation/REPRODUCIBILITY.md`.
