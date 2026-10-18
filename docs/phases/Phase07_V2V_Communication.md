# Phase 07 — V2V communication

Add a Veins CAV application module that performs authenticated ML-KEM session
establishment, derives an AEAD key with transcript binding, and protects
CAM/BSM-like safety payloads. Associated data contains pseudonym, timestamp,
and message type.

**Complete when:** end-to-end V2V latency, PDR, bytes, replay detection, and
forgery rejection are collected without exposing safety decisions to PBFT wait
time.
