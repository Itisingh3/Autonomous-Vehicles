#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$ROOT"
mkdir -p results/raw/proverif results/summary results/plots
LOG=docs/evaluation/validation_log.md
printf '# Validation log\n\nStarted: %s\n' "$(date --iso-8601=seconds)" > "$LOG"
step(){ name="$1"; shift; start=$(date --iso-8601=seconds); echo "[$start] START $name" | tee -a "$LOG"; if "$@" >>"$LOG" 2>&1; then status=0; else status=$?; fi; end=$(date --iso-8601=seconds); echo "[$end] END $name status=$status" | tee -a "$LOG"; ((status==0)) || exit "$status"; }
step "OMNeT++ build" bash -lc "cd '$ROOT/simulation/omnetpp' && make MODE=release -j2"
step "SUMO validation" sumo -c "$ROOT/simulation/sumo/validation.sumocfg" --seed 42 --duration-log.statistics
step "handover campaign" bash "$ROOT/simulation/omnetpp/run_handover_campaign.sh" --seeds 20 --speeds 30,50,80 --densities 50,100,200,300 --spacings 250,400
step "handover aggregation" python3 "$ROOT/simulation/omnetpp/aggregate_handover_campaign.py" --input "$ROOT/results/raw/omnetpp_handover_campaign.csv" --output "$ROOT/results/raw/omnetpp_handover_campaign_summary.csv"
step "handover plot" python3 "$ROOT/simulation/omnetpp/plot_handover_campaign.py" --input "$ROOT/results/raw/omnetpp_handover_campaign_summary.csv" --output "$ROOT/results/plots/handover_latency_comparison.png"
step "crypto benchmark" bash "$ROOT/crypto/tests/run_crypto_benchmark.sh"
step "ProVerif" bash "$ROOT/proverif/run_all.sh"
step "PBFT validation" python3 "$ROOT/experiments/run_pbft_validation.py" --seeds 20 --output "$ROOT/results/raw/pbft_validation.csv"
step "PBFT aggregation" python3 "$ROOT/experiments/aggregate_pbft_validation.py" --input "$ROOT/results/raw/pbft_validation.csv" --output "$ROOT/results/summary/pbft_validation_summary.csv"
step "unit tests" python3 -m pytest -q
echo "Validation pipeline completed." | tee -a "$LOG"
