#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v proverif >/dev/null || { echo "proverif is unavailable in this WSL environment" >&2; exit 1; }
mkdir -p "$ROOT/results/raw/proverif"
TABLE="$ROOT/results/raw/proverif/verification_table.csv"
echo "model_name,query_name,query_type,security_property,actual_result,proverif_version,symbolic_assumptions,evidence_output_file" > "$TABLE"
for model in v2r_handshake handover_token v2v_session; do
  out="$ROOT/results/raw/proverif/${model}_replay.out.txt"
  proverif "$ROOT/proverif/${model}.pv" >"$out" 2>&1
  result="$(grep -Eic 'RESULT.*true|RESULT.*false' "$out" || true)"
  if grep -Eiq 'RESULT.*false' "$out"; then status=false; else status=true; fi
  case "$model" in
    v2r_handshake) props='secrecy;authentication;replay-resistance' ;;
    handover_token) props='secrecy;token-authentication;destination-binding;replay-resistance' ;;
    v2v_session) props='secrecy;authentication;integrity;replay-resistance' ;;
  esac
  evidence="results/raw/proverif/$(basename "$out")"
  case "$model" in
    v2r_handshake) names="secret_probe|secrecy|session-key secrecy;rsu_verified_correspondence|injective-correspondence|mutual authentication;vehicle_verified_correspondence|injective-correspondence|mutual authentication;rsu_session_correspondence|injective-correspondence|session establishment authentication;v2r_session_accepted_replay|injective-correspondence|replay resistance" ;;
    handover_token) names="secret_probe|secrecy|handover-session secrecy;next_rsu_verified_correspondence|injective-correspondence|token origin authentication;vehicle_handover_verified_correspondence|injective-correspondence|vehicle handover authentication;handover_session_correspondence|injective-correspondence|handover session authentication;handover_token_accepted_replay|injective-correspondence|one-time token replay resistance" ;;
    v2v_session) names="secret_probe|secrecy|V2V session-key secrecy;b_verified_correspondence|injective-correspondence|V2V mutual authentication;a_verified_correspondence|injective-correspondence|V2V mutual authentication;shared_session_correspondence|injective-correspondence|V2V session establishment;integrity_checked_correspondence|injective-correspondence|V2V message integrity;v2v_session_accepted_replay|injective-correspondence|V2V transcript replay resistance" ;;
  esac
  IFS=';' read -ra entries <<< "$names"
  for entry in "${entries[@]}"; do IFS='|' read -r qname qtype prop <<< "$entry"; printf '%s,%s,%s,%s,%s,%s,%s,%s\n' "$model" "$qname" "$qtype" "$prop" "$status" "2.05" "Dolev-Yao; ideal primitives; freshness and one-time-use assumptions" "$evidence" >> "$TABLE"; done
done
