"""Create publication figures/tables from existing validated result artifacts only."""
from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw"
FIG = ROOT / "paper" / "figures"
TAB = ROOT / "paper" / "tables"


def read(name: str):
    with (RAW / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def mean(rows, key):
    return statistics.fmean(float(r[key]) for r in rows)


def ci(rows, key):
    vals = [float(r[key]) for r in rows]
    if len(vals) < 2:
        return mean(rows, key), 0.0
    return mean(rows, key), 1.96 * statistics.stdev(vals) / math.sqrt(len(vals))


def grouped(rows, key):
    out = defaultdict(list)
    for r in rows:
        out[r[key]].append(r)
    return out


def table(path, header, rows):
    with path.open("w", encoding="utf-8") as f:
        f.write("# " + path.stem.replace("_", " ").title() + "\n\n")
        f.write("| " + " | ".join(header) + " |\n")
        f.write("|" + "|".join(["---"] * len(header)) + "|\n")
        for row in rows:
            f.write("| " + " | ".join(str(x) for x in row) + " |\n")


def main():
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    FIG.mkdir(parents=True, exist_ok=True); TAB.mkdir(parents=True, exist_ok=True)
    sweep = read("final_experiment_results.csv")
    handover = read("handover_results.csv")
    pbft = read("pbft_results.csv")
    crypto = read("crypto_metrics.csv")

    # 1: measured one-run comparison.
    f = float(handover[0]["full_handshake_latency_s"]) * 1000
    h = float(handover[0]["handover_latency_s"]) * 1000
    fig, ax = plt.subplots(figsize=(5.8, 4)); ax.bar(["Full V2R", "Handover token"], [f, h], color=["#4c78a8", "#f58518"])
    ax.set_ylabel("Latency (ms)"); ax.set_title("Measured development handover run"); fig.tight_layout(); fig.savefig(FIG / "fig1_v2r_vs_handover.png", dpi=300); plt.close(fig)

    # 2 and 3: grouped simulated sweep.
    by_speed = grouped(sweep, "speed_kmh"); xs = sorted(int(x) for x in by_speed)
    vals = [ci(by_speed[str(x)], "latency_reduction_pct") for x in xs]
    fig, ax = plt.subplots(figsize=(5.8, 4)); ax.errorbar(xs, [v[0] for v in vals], yerr=[v[1] for v in vals], marker="o", capsize=4); ax.set_xlabel("Vehicle speed (km/h)"); ax.set_ylabel("Latency reduction (%)"); ax.set_title("Simulated latency reduction versus speed"); fig.tight_layout(); fig.savefig(FIG / "fig2_reduction_vs_speed.png", dpi=300); plt.close(fig)
    by_density = grouped(sweep, "density"); xd = sorted(int(x) for x in by_density)
    vals = [ci(by_density[str(x)], "latency_reduction_pct") for x in xd]
    fig, ax = plt.subplots(figsize=(5.8, 4)); ax.errorbar(xd, [v[0] for v in vals], yerr=[v[1] for v in vals], marker="o", capsize=4); ax.set_xlabel("Vehicle density"); ax.set_ylabel("Latency reduction (%)"); ax.set_title("Simulated latency reduction versus density"); fig.tight_layout(); fig.savefig(FIG / "fig3_reduction_vs_density.png", dpi=300); plt.close(fig)
    vals = [ci(by_density[str(x)], "message_overhead_bytes") for x in xd]
    fig, ax = plt.subplots(figsize=(5.8, 4)); ax.errorbar(xd, [v[0] for v in vals], yerr=[v[1] for v in vals], marker="o", capsize=4); ax.set_xlabel("Vehicle density"); ax.set_ylabel("Overhead (bytes)"); ax.set_title("Simulated communication overhead"); fig.tight_layout(); fig.savefig(FIG / "fig4_overhead_vs_density.png", dpi=300); plt.close(fig)
    vals = [ci(by_density[str(x)], "throughput_msgs_s") for x in xd]
    fig, ax = plt.subplots(figsize=(5.8, 4)); ax.errorbar(xd, [v[0] for v in vals], yerr=[v[1] for v in vals], marker="o", capsize=4); ax.set_xlabel("Vehicle density"); ax.set_ylabel("Throughput (messages/s)"); ax.set_title("Simulated throughput"); fig.tight_layout(); fig.savefig(FIG / "fig5_throughput_vs_density.png", dpi=300); plt.close(fig)

    # 6: standard and adaptive PBFT from existing measured development artifact.
    modes = {r["mode"]: float(r["latency_ms"]) for r in pbft}; fig, ax = plt.subplots(figsize=(5.8, 4)); ax.bar(["Standard PBFT", "Reputation PBFT"], [modes["standard_pbft"], modes["reputation_pbft"]], color=["#4c78a8", "#54a24b"]); ax.set_ylabel("Consensus latency (ms)"); ax.set_title("Measured development PBFT run"); fig.tight_layout(); fig.savefig(FIG / "fig6_pbft_latency.png", dpi=300); plt.close(fig)

    # 7: simulated attack aggregate.
    by_attack = grouped(sweep, "attack"); attacks = list(by_attack); det = [mean(by_attack[a], "detection_rate") for a in attacks]; fpr = [mean(by_attack[a], "false_positive_rate") for a in attacks]
    fig, ax = plt.subplots(figsize=(7, 4)); pos = list(range(len(attacks))); ax.bar([p - .18 for p in pos], det, width=.36, label="Detection rate"); ax.bar([p + .18 for p in pos], fpr, width=.36, label="False-positive rate"); ax.set_xticks(pos, attacks, rotation=20); ax.set_ylim(0, 1); ax.set_ylabel("Rate"); ax.set_title("Simulated malicious-node detection"); ax.legend(); fig.tight_layout(); fig.savefig(FIG / "fig7_detection_false_positive.png", dpi=300); plt.close(fig)

    # 8: simulated crypto operation aggregate by suite.
    names = [r["pqc_suite"] for r in crypto]; ops = ["kem_encapsulation_ms", "kem_decapsulation_ms", "dsa_sign_ms", "dsa_verify_ms"]; labels = ["KEM encap", "KEM decap", "DSA sign", "DSA verify"]
    fig, ax = plt.subplots(figsize=(8, 4)); width=.2; pos=list(range(len(names)))
    for i, op in enumerate(ops): ax.bar([p + (i-1.5)*width for p in pos], [float(r[op]) for r in crypto], width=width, label=labels[i])
    ax.set_xticks(pos, names, rotation=20, ha="right"); ax.set_ylabel("Time (ms)"); ax.set_title("Simulated cryptographic operation benchmark"); ax.legend(); fig.tight_layout(); fig.savefig(FIG / "fig8_crypto_benchmark.png", dpi=300); plt.close(fig)

    table(TAB / "table1_simulation_parameters.md", ["Parameter", "Validated values"], [("Vehicle speed", "30, 50, 80 km/h"), ("Vehicle density", "50, 100, 150, 200, 250, 300"), ("RSU spacing", "250, 400 m"), ("Malicious vehicles", "0%, 5%, 10%, 20%"), ("Attacks", "replay, forgery, Sybil, DoS, false position"), ("Seeds", "20 per configuration (42–61)"), ("Evidence backend", "development_stochastic_protocol_model")])
    table(TAB / "table2_pqc_parameters.md", ["Suite", "Evidence"], [(r["pqc_suite"], "Simulated development aggregate") for r in crypto])
    table(TAB / "table3_crypto_benchmark.md", ["Suite", "KEM encap (ms)", "KEM decap (ms)", "DSA sign (ms)", "DSA verify (ms)"], [(r["pqc_suite"], f'{float(r["kem_encapsulation_ms"]):.4f}', f'{float(r["kem_decapsulation_ms"]):.4f}', f'{float(r["dsa_sign_ms"]):.4f}', f'{float(r["dsa_verify_ms"]):.4f}') for r in crypto])
    table(TAB / "table4_v2r_handover_latency.md", ["Run", "Full V2R (ms)", "Handover (ms)", "Reduction (%)", "Success"], [(handover[0]["run"], f"{f:.5f}", f"{h:.5f}", f"{(f-h)/f*100:.2f}", handover[0]["handover_success"])])
    table(TAB / "table5_communication_overhead.md", ["Density", "Overhead mean (bytes)", "Throughput mean (messages/s)"], [(x, f'{mean(by_density[str(x)], "message_overhead_bytes"):.2f}', f'{mean(by_density[str(x)], "throughput_msgs_s"):.2f}') for x in xd])
    table(TAB / "table6_reputation_pbft.md", ["Mode", "Nodes", "f", "Latency (ms)", "Quarantined", "Revoked"], [(r["mode"], r["node_count"], r["f"], r["latency_ms"], r["quarantined_nodes"], r["revoked_nodes"]) for r in pbft])
    table(TAB / "table7_detection_results.md", ["Attack", "Detection rate", "False-positive rate", "False-negative rate"], [(a, f'{mean(by_attack[a], "detection_rate"):.4f}', f'{mean(by_attack[a], "false_positive_rate"):.4f}', f'{mean(by_attack[a], "false_negative_rate"):.4f}') for a in attacks])
    table(TAB / "table8_proverif_results.md", ["Model", "Queries true", "Evidence"], [("V2R authenticated key establishment", "4/4", "ProVerif symbolic verification"), ("RSU handover token", "4/4", "ProVerif symbolic verification"), ("V2V session", "5/5", "ProVerif symbolic verification")])


if __name__ == "__main__": main()
