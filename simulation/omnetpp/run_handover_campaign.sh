#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SEEDS=20; SPEEDS="30,50,80"; DENSITIES="50,100,200,300"; SPACINGS="250,400"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --seeds) SEEDS="$2"; shift 2;;
    --speeds) SPEEDS="$2"; shift 2;;
    --densities) DENSITIES="$2"; shift 2;;
    --spacings) SPACINGS="$2"; shift 2;;
    *) echo "unknown argument: $1" >&2; exit 2;;
  esac
done
if command -v opp_run >/dev/null; then
  USE_OPP_ENV=0
else
  command -v opp_env >/dev/null || { echo "opp_run and opp_env are unavailable" >&2; exit 1; }
  USE_OPP_ENV=1
fi
[[ -x "$ROOT/simulation/omnetpp/cav_pqc_network" ]] || { echo "cav_pqc_network is not built" >&2; exit 1; }
mkdir -p "$ROOT/results/raw/handover_logs"
OUT="$ROOT/results/raw/omnetpp_handover_campaign.csv"
echo "seed,speed_kmh,density,rsu_spacing_m,status,log,full_handshake_latency_s,handover_latency_s,handover_success,fallback_used,transition_count" > "$OUT"
IFS=',' read -ra SPEED_LIST <<< "$SPEEDS"; IFS=',' read -ra DENSITY_LIST <<< "$DENSITIES"; IFS=',' read -ra SPACING_LIST <<< "$SPACINGS"
for ((seed=42; seed<42+SEEDS; seed++)); do
  for speed in "${SPEED_LIST[@]}"; do for density in "${DENSITY_LIST[@]}"; do for spacing in "${SPACING_LIST[@]}"; do
    id="${seed}_${speed}_${density}_${spacing}"; log="$ROOT/results/raw/handover_logs/${id}.log"
    tmpini="$(mktemp "$ROOT/simulation/omnetpp/.validation.XXXXXX.ini")"
    sed -e "s/^seed-set = .*/seed-set = $seed/" \
        -e "s/vehicleSpeed=50/vehicleSpeed=$speed/" \
        -e "s/rsuSpacing=400/rsuSpacing=$spacing/" \
        "$ROOT/simulation/omnetpp/omnetpp_validation.ini" > "$tmpini"
    rm -f "$ROOT/results/raw/handover_results.csv"
    VEINS_ROOT="${VEINS_ROOT:-/home/opp_env/veins}"
    if [[ "$USE_OPP_ENV" -eq 1 ]]; then
      simcmd="./cav_pqc_network -u Cmdenv -n .:../.neddeps:${VEINS_ROOT}/src -f '$tmpini' -c General"
      if (cd "$ROOT/simulation/omnetpp" && opp_env run omnetpp-6.0.1 -c "$simcmd") >"$log" 2>&1; then status=success; else status=failed; fi
    else
      if (cd "$ROOT/simulation/omnetpp" && ./cav_pqc_network -u Cmdenv -n ".:../.neddeps:${VEINS_ROOT}/src" -f "$tmpini" -c General) >"$log" 2>&1; then status=success; else status=failed; fi
    fi
    rm -f "$tmpini"
    full=""; handover=""; success=""; fallback=""; transitions=0
    if [[ -f "$ROOT/results/raw/handover_results.csv" ]]; then
      IFS=',' read -r _ full handover success fallback < <(tail -n 1 "$ROOT/results/raw/handover_results.csv")
      transitions=$(awk -F',' 'NR>1 && $4==1 {n++} END{print n+0}' "$ROOT/results/raw/handover_results.csv")
    fi
    echo "$seed,$speed,$density,$spacing,$status,$log,$full,$handover,$success,$fallback,$transitions" >> "$OUT"
    [[ "$status" == success ]] || { echo "failed run $id; see $log" >&2; exit 1; }
  done; done; done; done
echo "Campaign run index written to $OUT"
