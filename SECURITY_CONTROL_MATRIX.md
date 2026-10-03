# Day 34 Security Control Matrix

| Control | Attack addressed | Implementation | Verification |
|---|---|---|---|
| Passport signature | Identity forgery/tampering | Ed25519 | signing/evidence tests |
| Fingerprint binding | Evidence substitution | SHA-256 canonical identity | evidence tests |
| Capability negotiation | Runtime mismatch | explicit required/provided capabilities | negotiation tests |
| Permission policy | Unauthorized tool use | allow/deny, deny-overrides-allow | security tests |
| Delegation scope | Privilege escalation | scoped capabilities/tools | delegation-security tests |
| Expiry/max-use | Stale authorization | bounded token lifetime/use | delegation-security tests |
| Replay guard | Request replay | nonce cache | hardening tests |
| Rate limiter | Flooding | per-principal sliding window | hardening tests |
| Request guard | Malformed/oversized input | validation + size limit | hardening tests |
| Secret redaction | Credential exposure | recursive redaction | hardening tests |
| Audit chain | Log tampering | hash-linked entries | audit tests |
| Sandbox | Tool abuse | isolated process + resource limits | sandbox tests |
| Encrypted keystore | Private-key theft | PBKDF2 + AES-GCM | keystore tests |
| Registry verification | Stale/forged identity | signature/status checks | registry tests |
| Red-team suite | Control regression | local defensive probes | red-team tests |
