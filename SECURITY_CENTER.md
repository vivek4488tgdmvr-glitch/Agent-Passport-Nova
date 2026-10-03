# Security Center

The Security Center is a reviewer-facing view of the controls already implemented
in Agent Passport. It is an observability layer, not a replacement for authorization.

## Trust pipeline

1. Input validation
2. Rate limiting
3. Replay protection
4. Passport/signature verification
5. Capability and delegation checks
6. Tool permission checks
7. Sandbox execution
8. Secret redaction
9. Tamper-evident audit
10. Cryptographic evidence
11. Registry verification

## Reviewer rule

A green status means the corresponding local check/evidence passed. It does not
mean the system is invulnerable or that an external platform's private validator
has accepted the repository.
