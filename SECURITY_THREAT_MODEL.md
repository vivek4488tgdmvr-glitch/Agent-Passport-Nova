# Agent Passport — Security Threat Model

Day 34 turns the security work into an explicit threat model. This is a defensive reference model for the Agent Passport implementation; it does not claim that the system is unhackable.

## Assets

| Asset | Security property | Primary controls |
|---|---|---|
| Passport identity | Integrity/authenticity | Ed25519 signatures, fingerprints, registry verification |
| Private signing keys | Confidentiality | Encrypted keystore, restrictive file permissions, rotation |
| Delegation authority | Least privilege | Scoped capabilities/tools, expiry, max-use, replay protection |
| Tool execution | Isolation/authorization | Permission policy, sandbox, timeout/resource limits |
| Evidence | Integrity/provenance | Hashing, signatures, Passport-fingerprint binding |
| Audit records | Integrity/confidentiality | Tamper-evident chain, secret redaction |
| Registry records | Integrity/availability | Signature verification, revocation, versioning |

## Threats and mitigations

### T1 — Forged Passport
**Threat:** An attacker modifies identity/capabilities and presents the result as an authentic Passport.

**Mitigations:** signed Passport verification, deterministic fingerprinting, registry verification.

**Residual risk:** Trust in the issuer/public-key distribution is an operational concern.

### T2 — Delegation replay
**Threat:** A previously valid delegation request/token is reused.

**Mitigations:** nonce/replay guard, expiry, maximum-use enforcement, purpose binding.

**Residual risk:** A distributed deployment needs persistent/transactional replay state.

### T3 — Privilege escalation
**Threat:** A delegated agent requests capabilities or tools outside its authorized scope.

**Mitigations:** explicit capability/tool scopes, deny-by-default permissions, escalation checks.

### T4 — Malicious tool execution
**Threat:** A compromised agent attempts shell/filesystem/network abuse through a tool.

**Mitigations:** permission checks before execution and sandbox resource limits.

**Residual risk:** The reference Python subprocess sandbox is not a hostile-code boundary equivalent to a microVM/kernel sandbox.

### T5 — Credential leakage
**Threat:** Secrets appear in logs, evidence, or source/configuration.

**Mitigations:** recursive secret redaction, release-tree secret scanning, encrypted keystore, environment/secure-storage boundaries.

### T6 — Audit tampering
**Threat:** An attacker modifies a historical audit event.

**Mitigations:** hash-linked audit records and verification tests.

**Residual risk:** Persistent audit storage and its signing/transport boundary must be protected in production.

### T7 — Request flooding
**Threat:** A caller exhausts verification or tool resources.

**Mitigations:** per-principal sliding-window rate limiting, request-size limits, execution timeouts.

### T8 — Registry substitution/revocation bypass
**Threat:** A stale or revoked Passport is treated as current trusted identity.

**Mitigations:** active-status checks, signature verification during retrieval, version lookup, revocation state.

## Security decision flow

```text
UNTRUSTED REQUEST
      |
      v
Input validation --> reject malformed/oversized input
      |
      v
Rate limit -------> reject abusive traffic
      |
      v
Replay check ------> reject reused request/token
      |
      v
Passport signature -> reject unauthenticated/tampered identity
      |
      v
Capability + delegation scope
      |
      v
Permission policy --> deny unauthorized tool/action
      |
      v
Sandbox execution
      |
      v
Secret redaction + audit
      |
      v
Cryptographic evidence
```

## Security claims we do not make

- No claim of being unhackable.
- No claim that a Python subprocess is a complete hostile-code sandbox.
- No claim that a signature alone establishes issuer trust.
- No claim that local checkpoint/visa adapters reproduce a private challenge validator.

Production deployment should add TLS/mutual authentication where appropriate, OS/container or microVM isolation, restricted network egress, persistent replay state, protected audit storage, centralized secret management, monitoring, patching, and incident response.
