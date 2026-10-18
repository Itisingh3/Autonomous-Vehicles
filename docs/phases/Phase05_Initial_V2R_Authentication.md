# Phase 05 — Initial V2R authentication

Implement signed HELLO, signed challenge containing ML-KEM ciphertext, and
Finished confirmation. Bind pseudonyms, credential references, timestamps,
nonces, suite identifier, KEM values, and both protocol messages in the
transcript.

**Complete when:** valid sessions agree on a key; replay, forged signatures,
suite splicing, and corrupted ciphertext fail closed.
