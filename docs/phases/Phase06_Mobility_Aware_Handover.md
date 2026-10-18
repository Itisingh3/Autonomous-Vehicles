# Phase 06 — Mobility-aware handover

The serving RSU predicts the next RSU and issues a short-lived, one-time
ML-DSA-signed token bound to pseudonym, target RSU, hashed context, nonce, and
time range. The next RSU requires a fresh vehicle signature and derives a fresh
session; invalid/expired/replayed tokens fall back to Phase 05.

**Complete when:** the C++ smoke test rejects replay and wrong-target tokens;
Veins experiments compare token and full-handshake latency over paired seeds.
