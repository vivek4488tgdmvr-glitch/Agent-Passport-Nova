# Agent Passport — Day 30 Security Audit

Day 30 is the final **local defensive security gate** for the competition build.
It validates the controls implemented during Days 26–29 without scanning or
attacking external systems.

## Audit controls

1. Full test suite with **zero skipped tests**.
2. Safe local red-team probes.
3. Encrypted cryptographic key-management implementation.
4. Tool sandbox enforcement.
5. Request validation, rate limiting, replay protection and tamper-evident audit.
6. Cryptographically signed Passport Travel evidence verification.
7. No private-key material files in the release tree.
8. No high-confidence live-secret patterns in application/config files.
9. Cryptography dependency declaration.
10. Required release artifacts.

Run:

```bash
python examples/day30_security_audit.py
```

The audit writes `security-audit-report.json`.

## What this does not claim

Passing this audit does **not** mean the system is unhackable. A production
deployment still needs TLS, authenticated service boundaries, protected secret
storage, OS/container/microVM isolation for hostile code, restricted network
egress,
patch management, centralized protected logging, and independent penetration
testing.

The audit is intentionally limited to the repository's own deterministic,
defensive controls.
