#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v proverif >/dev/null || { echo "proverif is unavailable in this WSL environment" >&2; exit 1; }
mkdir -p "$ROOT/results/raw/proverif"
TABLE="$ROOT/results/raw/proverif/verification_table.csv"
echo "model,query,result,output_file" > "$TABLE"
for model in v2r_handshake handover_token v2v_session; do
  out="$ROOT/results/raw/proverif/${model}.out.txt"
  proverif "$ROOT/proverif/${model}.pv" >"$out" 2>&1
  grep -E "RESULT|true|false" "$out" | while IFS= read -r line; do
    safe=$(printf '%s' "$line" | tr ',' ';'); printf '%s,%s,%s\n' "$model" "$safe" "recorded in $out" >> "$TABLE"
  done || true
done
