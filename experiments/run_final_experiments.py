"""Reproducible development experiment sweep for the CAV protocol.

This driver produces development evidence from a deterministic stochastic model of
the already implemented protocol stages.  It is intentionally explicit about the
measurement source; replace ``simulate_row`` with OMNeT++/Veins batch execution
before using numerical values in a paper.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
PLOTS = ROOT / "results" / "plots"
TABLES = ROOT / "paper" / "tables"
FIGURES = ROOT / "paper" / "figures"

SUITES = {
    "ML-KEM-512+ML-DSA-44": {"kem": 1.00, "dsa": 1.00, "overhead": 1.00},
    "ML-KEM-768+ML-DSA-65": {"kem": 1.22, "dsa": 1.18, "overhead": 1.22},
    "ML-KEM-1024+ML-DSA-87": {"kem": 1.48, "dsa": 1.42, "overhead": 1.48},
}
ATTACKS = ("replay", "forgery", "sybil", "dos", "false_position")
SPEEDS = (30, 50, 80)
DENSITIES = (50, 100, 150, 200, 250, 300)
SPACINGS = (250, 400)
MALICIOUS = (0, 5, 10, 20)


def ci95(values: list[float]) -> tuple[float, float, float]:
    mean = statistics.fmean(values)
    if len(values) < 2:
        return mean, 0.0, 0.0
    half = 1.96 * statistics.stdev(values) / math.sqrt(len(values))
    return mean, half, mean - half


def simulate_row(speed: int, density: int, spacing: int, suite: str, malicious: int,
                 attack: str, seed: int) -> dict[str, float | int | str]:
    rng = random.Random(seed)
    factors = SUITES[suite]
    density_factor = 1.0 + density / 1000.0
    mobility_factor = 1.0 + speed / 800.0
    spacing_factor = 1.0 + (400 - spacing) / 2000.0
    attack_penalty = {"replay": .03, "forgery": .02, "sybil": .06,
                      "dos": .14, "false_position": .08}[attack]
    threat = malicious / 100.0
    kem_encap = 0.42 * factors["kem"] * (1 + rng.uniform(-.06, .06))
    kem_decap = 0.38 * factors["kem"] * (1 + rng.uniform(-.06, .06))
    dsa_sign = 0.31 * factors["dsa"] * (1 + rng.uniform(-.06, .06))
    dsa_verify = 0.22 * factors["dsa"] * (1 + rng.uniform(-.06, .06))
    full = (2.1 * density_factor * mobility_factor + kem_encap + kem_decap
            + dsa_sign + dsa_verify) * (1 + rng.uniform(-.05, .05))
    handover = (.62 * spacing_factor * mobility_factor + dsa_sign + dsa_verify
                + .18 * factors["kem"]) * (1 + rng.uniform(-.05, .05))
    reduction = 100.0 * (full - handover) / full
    overhead = 920.0 * factors["overhead"] + density * .35 + (80 if attack == "sybil" else 0)
    pdr = max(0.0, min(1.0, .995 - density / 5000.0 - threat * .20 - attack_penalty
                        + rng.gauss(0, .006)))
    throughput = max(0.1, (pdr * 1000.0) / (full + density * .012))
    consensus_standard = (4.5 + density * .012 + threat * 8 + rng.uniform(-.25, .25))
    consensus_reputation = consensus_standard * (0.90 - min(threat, .2) * .20) + rng.uniform(-.2, .2)
    detection = max(0.0, min(1.0, .74 + threat * 1.0 + attack_penalty * 1.4 + rng.gauss(0, .025)))
    false_positive = max(0.0, min(1.0, .018 + density / 30000.0 + (0.012 if attack == "dos" else 0) + rng.gauss(0, .004)))
    false_negative = max(0.0, min(1.0, 1.0 - detection + rng.gauss(0, .01)))
    return {
        "seed": seed, "speed_kmh": speed, "density": density, "rsu_spacing_m": spacing,
        "pqc_suite": suite, "malicious_pct": malicious, "attack": attack,
        "full_handshake_latency_ms": full, "handover_latency_ms": handover,
        "latency_reduction_pct": reduction, "kem_encapsulation_ms": kem_encap,
        "kem_decapsulation_ms": kem_decap, "dsa_sign_ms": dsa_sign,
        "dsa_verify_ms": dsa_verify, "message_overhead_bytes": overhead,
        "throughput_msgs_s": throughput, "packet_delivery_ratio": pdr,
        "consensus_latency_standard_ms": consensus_standard,
        "consensus_latency_reputation_ms": consensus_reputation,
        "detection_rate": detection, "false_positive_rate": false_positive,
        "false_negative_rate": false_negative,
        "measurement_source": "development_stochastic_protocol_model",
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def aggregate(rows: list[dict]) -> list[dict]:
    dimensions = ["speed_kmh", "density", "rsu_spacing_m", "pqc_suite", "malicious_pct", "attack"]
    metrics = ["full_handshake_latency_ms", "handover_latency_ms", "latency_reduction_pct",
               "kem_encapsulation_ms", "kem_decapsulation_ms", "dsa_sign_ms", "dsa_verify_ms",
               "message_overhead_bytes", "throughput_msgs_s", "packet_delivery_ratio",
               "consensus_latency_standard_ms", "consensus_latency_reputation_ms",
               "detection_rate", "false_positive_rate", "false_negative_rate"]
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[d] for d in dimensions)].append(row)
    out = []
    for key, values in groups.items():
        base = dict(zip(dimensions, key)); base["n_seeds"] = len(values)
        for metric in metrics:
            mean, half, lower = ci95([float(v[metric]) for v in values])
            base[f"{metric}_mean"] = mean; base[f"{metric}_ci95_halfwidth"] = half
            base[f"{metric}_ci95_low"] = lower; base[f"{metric}_ci95_high"] = mean + half
        out.append(base)
    return out


def make_outputs(rows: list[dict], summary: list[dict]) -> None:
    write_csv(RAW / "final_experiment_results.csv", rows)
    write_csv(RAW / "final_experiment_summary.csv", summary)
    crypto = [{"pqc_suite": name, "kem_encapsulation_ms": statistics.fmean(float(r["kem_encapsulation_ms"]) for r in rows if r["pqc_suite"] == name),
               "kem_decapsulation_ms": statistics.fmean(float(r["kem_decapsulation_ms"]) for r in rows if r["pqc_suite"] == name),
               "dsa_sign_ms": statistics.fmean(float(r["dsa_sign_ms"]) for r in rows if r["pqc_suite"] == name),
               "dsa_verify_ms": statistics.fmean(float(r["dsa_verify_ms"]) for r in rows if r["pqc_suite"] == name)} for name in SUITES]
    write_csv(RAW / "crypto_metrics.csv", crypto)
    pbft = []
    for mode in ("standard_pbft", "reputation_pbft"):
        for row in summary:
            pbft.append({"mode": mode, "speed_kmh": row["speed_kmh"], "density": row["density"],
                         "malicious_pct": row["malicious_pct"], "attack": row["attack"],
                         "consensus_latency_ms": row[f"consensus_latency_{'standard' if mode == 'standard_pbft' else 'reputation'}_ms_mean"]})
    write_csv(RAW / "pbft_comparison.csv", pbft)
    TABLES.mkdir(parents=True, exist_ok=True)
    with (TABLES / "final_experiment_metrics.md").open("w", encoding="utf-8") as h:
        h.write("# Final experiment metrics\n\n")
        h.write("Values are means with 95% confidence intervals over the configured seeds.\n\n")
        h.write("| Suite | Speed | Density | Malicious | Attack | Full ms | Handover ms | Reduction % | PDR | Detection |\n|---|---:|---:|---:|---|---:|---:|---:|---:|---:|\n")
        for row in summary[:60]:
            h.write(f"| {row['pqc_suite']} | {row['speed_kmh']} | {row['density']} | {row['malicious_pct']} | {row['attack']} | {row['full_handshake_latency_ms_mean']:.3f} ± {row['full_handshake_latency_ms_ci95_halfwidth']:.3f} | {row['handover_latency_ms_mean']:.3f} ± {row['handover_latency_ms_ci95_halfwidth']:.3f} | {row['latency_reduction_pct_mean']:.2f} | {row['packet_delivery_ratio_mean']:.4f} | {row['detection_rate_mean']:.4f} |\n")
    with (TABLES / "crypto_metrics.md").open("w", encoding="utf-8") as h:
        h.write("# Cryptographic operation metrics\n\n| Suite | KEM encapsulation (ms) | KEM decapsulation (ms) | ML-DSA signing (ms) | ML-DSA verification (ms) |\n|---|---:|---:|---:|---:|\n")
        for row in crypto:
            h.write(f"| {row['pqc_suite']} | {row['kem_encapsulation_ms']:.4f} | {row['kem_decapsulation_ms']:.4f} | {row['dsa_sign_ms']:.4f} | {row['dsa_verify_ms']:.4f} |\n")
    with (TABLES / "pbft_comparison.md").open("w", encoding="utf-8") as h:
        h.write("# PBFT comparison\n\nThe CSV contains the complete factorial comparison.\n\n| Mode | Mean consensus latency (ms) |\n|---|---:|\n")
        for mode, metric in (("standard_pbft", "consensus_latency_standard_ms"), ("reputation_pbft", "consensus_latency_reputation_ms")):
            h.write(f"| {mode} | {statistics.fmean(float(r[metric]) for r in rows):.4f} |\n")
    with (ROOT / "results" / "summary.md").open("w", encoding="utf-8") as h:
        h.write("# Final experiment pipeline summary\n\n")
        h.write(f"Generated {len(rows)} seed-level observations and {len(summary)} grouped estimates.\n\n")
        h.write("The sweep covers speeds 30/50/80 km/h, densities 50–300, RSU spacing 250/400 m, all three requested PQC suites, malicious rates 0/5/10/20%, five attacks, and 20–30 configurable seeds.\n\n")
        h.write("**Measurement status:** these outputs come from `development_stochastic_protocol_model`, not an OMNeT++/Veins execution. They are reproducibility artifacts for pipeline validation and must not be presented as real network measurements until the batch simulator backend is connected.\n")
    try:
        import matplotlib.pyplot as plt
        PLOTS.mkdir(parents=True, exist_ok=True); FIGURES.mkdir(parents=True, exist_ok=True)
        names = list(SUITES); reductions = [statistics.fmean(float(r["latency_reduction_pct"]) for r in rows if r["pqc_suite"] == n) for n in names]
        plt.figure(figsize=(7, 4)); plt.bar(names, reductions); plt.ylabel("Latency reduction (%)"); plt.xticks(rotation=20); plt.tight_layout(); plt.savefig(PLOTS / "latency_reduction_by_suite.png", dpi=160); plt.savefig(FIGURES / "latency_reduction_by_suite.png", dpi=160); plt.close()
        attacks = list(ATTACKS); rates = [statistics.fmean(float(r["detection_rate"]) for r in rows if r["attack"] == a) for a in attacks]
        plt.figure(figsize=(7, 4)); plt.bar(attacks, rates); plt.ylabel("Detection rate"); plt.xticks(rotation=20); plt.tight_layout(); plt.savefig(PLOTS / "detection_by_attack.png", dpi=160); plt.savefig(FIGURES / "detection_by_attack.png", dpi=160); plt.close()
        plt.figure(figsize=(7, 4)); plt.scatter([float(r["density"]) for r in rows[::max(1, len(rows)//3000)]], [float(r["handover_latency_ms"]) for r in rows[::max(1, len(rows)//3000)]], s=5, alpha=.3); plt.xlabel("Vehicle density"); plt.ylabel("Handover latency (ms)"); plt.tight_layout(); plt.savefig(PLOTS / "handover_latency_vs_density.png", dpi=160); plt.savefig(FIGURES / "handover_latency_vs_density.png", dpi=160); plt.close()
        standard = statistics.fmean(float(r["consensus_latency_standard_ms"]) for r in rows); adaptive = statistics.fmean(float(r["consensus_latency_reputation_ms"]) for r in rows)
        plt.figure(figsize=(5, 4)); plt.bar(["Standard PBFT", "Reputation PBFT"], [standard, adaptive]); plt.ylabel("Consensus latency (ms)"); plt.tight_layout(); plt.savefig(PLOTS / "pbft_comparison.png", dpi=160); plt.savefig(FIGURES / "pbft_comparison.png", dpi=160); plt.close()
    except ImportError:
        (ROOT / "results" / "summary.md").open("a", encoding="utf-8").write("\nPlots were skipped because matplotlib is unavailable.\n")


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--seeds", type=int, default=20); parser.add_argument("--seed-start", type=int, default=42); parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(); count = 2 if args.smoke else args.seeds
    if count < 20 and not args.smoke: raise SystemExit("Use at least 20 seeds for the final sweep (or --smoke for a pipeline check).")
    rows = []
    for speed in SPEEDS:
        for density in DENSITIES:
            for spacing in SPACINGS:
                for suite in SUITES:
                    for malicious in MALICIOUS:
                        for attack in ATTACKS:
                            for offset in range(count):
                                rows.append(simulate_row(speed, density, spacing, suite, malicious, attack, args.seed_start + offset))
    make_outputs(rows, aggregate(rows)); print(f"Generated {len(rows)} observations from {count} seeds per configuration.")


if __name__ == "__main__": main()
