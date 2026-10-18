# Phase 03 — Cryptographic primitives

Use ML-KEM-768 for session-key establishment and ML-DSA-65 for authentication,
integrity, and non-repudiation. Use maintained liboqs bindings/wrapper, never
home-grown lattice implementations. Derive keys from the shared secret and a
canonical transcript hash; protect application payloads with AEAD.

**Complete when:** valid and corrupt KEM paths, signing/verification, and size
and timing measurements pass in Python and C++ smoke tests.
