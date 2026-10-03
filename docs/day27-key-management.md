# Day 27 — Cryptographic Key Management

Agent Passport now supports encrypted-at-rest Ed25519 signing keys.

## Threats addressed

- plaintext private-key files
- accidental private-key disclosure in source/config artifacts
- unauthorized key loading with the wrong password
- unsafe replacement during key rotation

## Design

```text
Password
   ↓ PBKDF2-HMAC-SHA256 (salt + 600k iterations)
32-byte encryption key
   ↓ AES-256-GCM + authenticated metadata
Encrypted keystore
   ↓
Ed25519 private key (never stored plaintext)
```

The keystore stores the public key and cryptographic metadata in cleartext,
but the private key is encrypted. A wrong password fails authentication.
Writes are atomic and use restrictive `0600` permissions where supported.

## CLI

```bash
agent-passport keystore init .agent-passport/nova.keystore.json --issuer nova
agent-passport keystore public .agent-passport/nova.keystore.json
agent-passport keystore rotate .agent-passport/nova.keystore.json
```

The CLI prompts for passwords rather than accepting them as command-line
arguments, reducing exposure through shell history/process listings.

## Production note

For a high-value deployment, use a dedicated KMS/HSM or OS secret store and
short-lived signing credentials. This local keystore is a hardened local
fallback, not a replacement for enterprise key custody.

## Day 27 verification

The complete project test suite passes with **116 tests and 0 skips** in the
release environment. The Day 27 demo also verifies wrong-password rejection
and safe key rotation.
