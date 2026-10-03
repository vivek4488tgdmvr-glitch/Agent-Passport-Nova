# Day 26 — Cybersecurity Hardening

Agent Passport is designed to **reduce attack surface** rather than claim that a Python demo can make an agent immune to hackers.

## Threats addressed

- Request flooding / brute-force-style abuse → per-principal sliding-window rate limiting.
- Replay of request identifiers/nonces → bounded replay guard.
- Malformed or oversized input → fail-closed request guard with strict metadata limits.
- Credential leakage through logs → recursive secret redaction.
- Audit-log manipulation → SHA-256 hash-chain audit records.
- Authorization bypass → existing deny-by-default permission policy remains in force.
- Delegation abuse → existing expiration, scope, max-use, replay, and purpose checks remain in force.

## Secure pipeline

```text
Untrusted Request
       ↓
Input Validation
       ↓
Rate Limit
       ↓
Replay Check
       ↓
Passport Signature / Identity
       ↓
Capability + Tool Authorization
       ↓
Security Policy (DENY BY DEFAULT)
       ↓
Action
       ↓
Redacted Tamper-Evident Audit Event
```

## Important deployment guidance

1. Keep the dashboard bound to localhost unless it is placed behind authenticated TLS/reverse-proxy controls.
2. Never put API keys, private keys, passwords, or bearer tokens into Passport files or audit logs.
3. Use a real secret manager and rotate credentials outside the Passport registry.
4. Persist replay state and audit logs in a transactional shared store for multi-instance deployments.
5. Treat Passport signatures as integrity/authenticity evidence, not as proof that an issuer is trustworthy.
6. Keep dangerous capabilities such as shell execution and arbitrary filesystem writes disabled unless an explicit policy grants them.
7. Apply operating-system/container sandboxing in addition to application-level authorization.

This layer is defensive security engineering; it does not provide offensive hacking functionality.
