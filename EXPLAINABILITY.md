# Explainability

## What the agent does

Nova is a portable research-oriented agent contract. It accepts text input and
returns structured JSON. Its identity, capabilities, behavior contract, tool
contracts, runtime compatibility, and security controls are declared rather
than inferred at runtime.

## How decisions are represented

The project separates three layers:

1. **Identity and capabilities** — what the agent claims to be able to do.
2. **Behavior and tools** — what inputs, outputs, and tool contracts are
   permitted.
3. **Verification and security** — whether those claims can be validated and
   whether a requested action is authorized.

For deterministic demonstrations, behavior conformance cases provide explicit
expected outputs or expected failures. Model-backed behavior is treated as an
integration boundary and should use schemas/evaluators for production use.

## Data used

The core Passport does not require a user's private data. Demonstrations use
synthetic agent metadata and deterministic tool inputs. API credentials are
read from environment/secure key storage rather than committed to the
repository.

## Security decisions

Tool execution is subject to least-privilege authorization, replay protection,
rate limiting, secret redaction, audit integrity checks, and sandbox controls.
Cryptographic signatures establish integrity/authenticity relative to a known
public key; they do not by themselves establish that an issuer is trusted.

## Limitations

This repository is a reference implementation, not a claim of absolute
security. Hostile workloads require production isolation such as containers or
microVMs, OS-level MAC/seccomp controls, restricted network egress, protected
persistent audit storage, and an operational key-management system.

The root `agent.yaml` is a strict **challenge-facing compatibility profile**
for the OpenGAP 0.1.0 shape visible in the public challenge UI. It is not a
claim to reproduce any private HiDevs validator implementation.

## Day 34 security decision trace

A security-sensitive action follows an explicit sequence rather than a hidden model decision:

```text
request → validate → rate-limit → replay-check → verify identity
→ check capability/delegation → authorize tool → sandbox → audit
```

A rejection should identify the failed control (for example, `RATE_LIMITED`, `REPLAY_REJECTED`, `CAPABILITY_MISSING`, or `PERMISSION_DENIED`) without exposing credentials or private key material. This makes security decisions inspectable while keeping secrets out of evidence.
