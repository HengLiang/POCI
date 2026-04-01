# POCI Security Deployment Guide

## AMTC v0.4.1 Usage

- **dummy_rate**: ≤ 50/s (built‑in rate limiting)
- **direction ratio**: target 2.0–2.3:1 (center 2.05)
- **HMAC marker**: 64 bytes (32B HMAC + 32B Ed25519 signature placeholder)
- **entropy**: all dummy payloads forced to >7.95 bits/byte

## Zero‑Trust Channel Deployment Steps

1. **Node ID Derivation**  
   `node_id = sha256(Ed25519_pub_key)` (same as NRP)

2. **mTLS Certificate Generation**  
   Use `derive_node_cert(pubkey)` to obtain node‑specific certificate.

3. **Integration with AMTC**  
   Call `enforce_mtls_on_amtc(packet, node_cert)` before morphing.

4. **Audit Sidecar**  
   The `audit_sidecar` method checks HMAC markers and logs verification results.

## Merkle Audit Process

- Each leaf must contain `origin_type` and `weight_coefficient` (0.3 for AI_ASSISTED).
- Batch validation triggers alert if AI_ASSISTED ratio > 40%.
- Ancestor check rejects any data derived from AI_GENERATED.