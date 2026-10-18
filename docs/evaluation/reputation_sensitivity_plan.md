# Reputation sensitivity experiment

The sweep is rule-based and uses no machine learning. It evaluates `alpha={1,2,3}`, `beta_high={2,5,8}`, `gamma={1,2,3}`, `lambda_recent={.05,.10,.20}`, and `W={10,20,50}` across ten required scenarios and seeds 42–61 (20 seeds/configuration), producing 48,600 rows.

Outputs are `results/raw/reputation_sensitivity.csv`, `results/summary/reputation_sensitivity_summary.csv`, and the seven requested plots under `results/plots/`. Metrics include detection, false-positive/negative rates, quarantine/revocation/recovery times, honest removals, consensus latency, message count, throughput, and reputation trajectory.
