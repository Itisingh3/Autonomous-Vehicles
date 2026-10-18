#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT/crypto/tests"
make
mkdir -p "$ROOT/results/raw"
./crypto_benchmark --repetitions 1000 --output "$ROOT/results/raw/crypto_benchmark.csv"
