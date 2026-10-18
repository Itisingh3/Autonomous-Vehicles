# Simulation Concepts

## Tool roles

- **OMNeT++** provides discrete-event simulation and module/message scheduling.
- **Veins** supplies vehicular networking, IEEE 802.11p modules, mobility integration, and TraCI interfaces.
- **SUMO** supplies road traffic and vehicle mobility. The repository includes XML configurations, but a completed linked campaign is **NOT FOUND**.
- **liboqs/PqcCrypto** supplies the intended post-quantum operations. The broad CSV sweep uses a stochastic model and does not prove that it called liboqs for every row.

## Actual configuration values

| Parameter | Value | Unit | Source | Varied? |
|---|---:|---|---|---|
| Simulation time limit | 10 | s | `simulation/omnetpp/omnetpp.ini` | No in smoke config |
| Vehicle speed | 30, 50, 80 | km/h | `run_final_experiments.py` | Yes in stochastic sweep |
| Vehicle density | 50,100,150,200,250,300 | vehicles | `run_final_experiments.py` | Yes in stochastic sweep; ini default is 1 |
| RSU spacing | 250,400 | m | `run_final_experiments.py` | Yes in stochastic sweep; ini default 400 |
| RSU coverage | **NOT FOUND** as a single configured value | m | — | — |
| Token validity | 5 | s | `omnetpp.ini`, `RSUApp.cc` | No in recorded sweep |
| Maximum clock skew | 200 | ms | `omnetpp.ini` | No |
| 802.11p bitrate | 6 | Mbps | `omnetpp.ini` | No |
| TX power | 20 | mW | `omnetpp.ini` | No |
| Noise floor | -98 | dBm | `omnetpp.ini` | No |
| Minimum power | -110 | dBm | `omnetpp.ini` | No |
| Carrier frequency | 5.890e9 | Hz | `simulation/sumo/config-static.xml` | No |
| Path-loss alpha | 2.0 | dimensionless | `config-static.xml` | No |
| PQC suites | ML-KEM-512/768/1024 paired with ML-DSA-44/65/87 | — | `run_final_experiments.py` | Yes in stochastic sweep |
| Seeds in final CSV | 42,43 | seed IDs | `final_experiment_results.csv` | Only 2 actually present |
| Seeds in reputation matrix | 42–61 | seed IDs | `run_reputation_sensitivity.py` | 20 per case |
| Warm-up period | **NOT FOUND** | — | — | — |
| Simulation duration for SUMO campaign | **NOT FOUND** | — | — | — |

## Evidence separation

The V2R/handover C++ application measures simulated latency with `simTime()` and emits cryptographic processing signals using wall-clock timing. The broad experiment script computes protocol-like values from random factors and labels them `development_stochastic_protocol_model`; it is not equivalent to a network run. The one-row `handover_results.csv` is a development artifact. No actual Veins/SUMO output trace is present in `results/raw`.

## Methodological interpretation

The repository contains three distinct evidence layers: (1) unit/protocol tests and C++ smoke modules, (2) stochastic Python development sweeps, and (3) symbolic ProVerif models. They answer different questions and must not be combined as if they were one experiment. The final factorial CSV has 4,320 rows, 2,160 parameter groups, and only two seeds per group. Thus its confidence intervals are based on n=2, not the 20–30 seeds described by older documentation.
