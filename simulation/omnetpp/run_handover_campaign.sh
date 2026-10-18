#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SEEDS=20; SPEEDS="30,50,80"; DENSITIES="50,100,200,300"; SPACINGS="250,400"; MIN_RSUS=3
while [[ $# -gt 0 ]]; do
  case "$1" in
    --seeds) SEEDS="$2"; shift 2;;
    --speeds) SPEEDS="$2"; shift 2;;
    --densities) DENSITIES="$2"; shift 2;;
    --spacings) SPACINGS="$2"; shift 2;;
    --min-rsus) MIN_RSUS="$2"; shift 2;;
    *) echo "unknown argument: $1" >&2; exit 2;;
  esac
done
OPP_RUN_BIN="${OPP_RUN_BIN:-/home/opp_env/omnetpp-6.0.1/bin/opp_run}"
if [[ -x "$OPP_RUN_BIN" ]] || command -v opp_run >/dev/null; then
  USE_OPP_ENV=0
else
  command -v opp_env >/dev/null || { echo "opp_run and opp_env are unavailable" >&2; exit 1; }
  USE_OPP_ENV=1
fi
[[ -x "$ROOT/simulation/omnetpp/cav_pqc_network" ]] || { echo "cav_pqc_network is not built" >&2; exit 1; }
mkdir -p "$ROOT/results/raw/handover_logs"
OUT="$ROOT/results/raw/omnetpp_handover_campaign.csv"
echo "seed,speed_kmh,density,rsu_spacing_m,status,log,rsu_id,source_rsu,destination_rsu,transition_index,authentication_method,full_handshake_latency_s,handover_token_latency_s,latency_reduction_percent,handover_success,fallback_used,rsus_crossed,handover_transitions,message_overhead_bytes,packet_delivery_ratio,throughput_messages_per_second,cryptographic_wall_clock_us,simulated_network_time_s,mlkem_encapsulation_us,mlkem_decapsulation_us,mldsa_signing_us,mldsa_verification_us" > "$OUT"
IFS=',' read -ra SPEED_LIST <<< "$SPEEDS"; IFS=',' read -ra DENSITY_LIST <<< "$DENSITIES"; IFS=',' read -ra SPACING_LIST <<< "$SPACINGS"
for speed in "${SPEED_LIST[@]}"; do for density in "${DENSITY_LIST[@]}"; do for spacing in "${SPACING_LIST[@]}"; do
  valid=0; candidate=42; attempts=0; max_attempts=$((SEEDS*5))
  while (( valid < SEEDS && attempts < max_attempts )); do
    seed=$candidate; candidate=$((candidate+1)); attempts=$((attempts+1))
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
    full=""; handover=""; success=""; fallback=""; transitions=0; source=""; destination=""; simtime=""
    if [[ -f "$ROOT/results/raw/handover_results.csv" ]]; then
      IFS=',' read -r _ full handover success fallback _ source destination simtime < <(tail -n 1 "$ROOT/results/raw/handover_results.csv")
      transitions=$(awk -F',' 'NR>1 && $4==1 {n++} END{print n+0}' "$ROOT/results/raw/handover_results.csv")
    fi
    # The configured validation topology has five RSUs.  A valid campaign
    # sample must complete all four transitions so paired latency data are
    # not mixed with partial/fallback runs.
    if (( transitions < 4 )); then status=failed; fi
    if [[ "$status" == success && "$transitions" -ge 4 ]]; then
      while IFS=',' read -r runid rowfull rowhandover rowsuccess rowfallback transition rowsource rowdestination rowsimtime; do
        [[ "$runid" == "run" || -z "$runid" ]] && continue
        reduction=""
        if [[ "$rowsuccess" == "1" && "$rowfallback" == "0" && -n "$rowfull" && -n "$rowhandover" && "$rowhandover" != "-1" && "$rowfull" != "0" ]]; then
          reduction=$(awk -v f="$rowfull" -v h="$rowhandover" 'BEGIN{printf "%.8f", (f-h)*100.0/f}')
        fi
        row_source=$(printf 'rsu-%03d' "$transition")
        echo "$seed,$speed,$density,$spacing,success,$log,$rowdestination,$row_source,$rowdestination,$transition,handover_token,${rowfull},${rowhandover},${reduction},${rowsuccess},${rowfallback},$((transitions+1)),$transition,,,,${rowsimtime},,,,," >> "$OUT"
      done < <(tail -n +2 "$ROOT/results/raw/handover_results.csv")
      valid=$((valid+1))
    else
      echo "$seed,$speed,$density,$spacing,failed,$log,,,,,,,,,,,,,,,,,,," >> "$OUT"
      echo "skipping invalid seed $seed for speed=$speed density=$density spacing=$spacing; see $log" >&2
    fi
  done
  if (( valid < SEEDS )); then
    echo "unable to collect $SEEDS valid seeds for speed=$speed density=$density spacing=$spacing (valid=$valid attempts=$attempts)" >&2
    exit 1
  fi
done; done; done
echo "Campaign run index written to $OUT"
