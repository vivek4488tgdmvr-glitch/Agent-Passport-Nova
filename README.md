# Agent Passport (Nova)

Portable AI-agent identity, behavior contracts, security controls, and verification for the **Agent Passport Challenge (HiDevs x Lyzr)**.

## Quick start

```bash
pip install -r requirements.txt cryptography
python -m pytest -q                              # full suite
PYTHONPATH=. python examples/day32_checkpoints.py   # 3 OpenGAP checkpoints
PYTHONPATH=. python examples/day33_framework_visas.py  # 4 framework visas
```

## Challenge mapping

| Challenge item | Where it lives |
|---|---|
| Root `agent.yaml` (OpenGAP spec 0.1.0) | `agent.yaml` |
| Checkpoint 01 - Validate | `agent_passport/opengap/schema.py` |
| Checkpoint 02 - Explain | `EXPLAINABILITY.md` |
| Checkpoint 03 - Passport evidence (Ed25519-verified, bound to `passport.yaml`) | `passport-travel-evidence-signed.json` |
| Visas: OpenAI SDK, CrewAI, Claude Code, Lyzr | `agent_passport/visas/` |
| Security | `SECURITY_THREAT_MODEL.md`, `SECURITY_CONTROL_MATRIX.md` |

Per-day history is kept below as a changelog.

---

# Day 34 — Explainability + Security

The challenge-facing layer now includes deterministic export contracts for the four framework visa entries shown in the public submission UI: **OpenAI SDK, CrewAI, Claude Code, and Lyzr**.

Each adapter produces a framework-shaped artifact and an `ISSUED` visa bound to the Passport agent id and version. Visa artifacts contain no credentials.

```bash
PYTHONPATH=. python examples/day33_framework_visas.py
python -m pytest -q
```

Day 34 regression result: **144 passed, 0 skipped**.

> These are explicit compatibility/export contracts based on the framework names visible in the public challenge UI. They do not claim to be official third-party SDK exports or to reproduce a private HiDevs validator.

See [`docs/day33-framework-visas.md`](docs/day33-framework-visas.md).

---

# Day 31 — OpenGAP Compatibility

The repository now includes a root-level `agent.yaml` compatibility entrypoint for the OpenGAP `0.1.0` profile shown in the challenge UI. The richer `passport.yaml` remains the internal Agent Passport source of truth.

The local compatibility boundary validates identity, behavior, tools, framework targets, security declarations, and rejects unknown root fields. It also provides a deterministic Passport → `agent.yaml` exporter.

Run:

```bash
python examples/day31_opengap.py
python -m pytest -q
```

`EXPLAINABILITY.md` documents agent decisions, data usage, security controls, and limitations.

> The root `agent.yaml` is a challenge-facing compatibility profile; it does not claim to reproduce any private HiDevs validator implementation.

---

# 🏁 Day 25 — Final Competition Release

Agent Passport is now packaged with a single release gate that verifies the full trust pipeline.

```bash
python examples/final_release_check.py
```

This runs the complete test suite plus the Passport Travel, cryptographic evidence, advanced security, and registry demonstrations. The release report is written to `final-release-report.json`.

Expected release condition: **0 failed, 0 skipped**.

See [`SUBMISSION_CHECKLIST.md`](SUBMISSION_CHECKLIST.md) and [`docs/day25-final-release.md`](docs/day25-final-release.md) for the final submission flow.

---


## Day 21 — LangChain Test Hardening

The Day 21 test suite removes the previously skipped LangChain factory test.
The mandatory suite now executes the factory path on every run using a small
`RunnableLambda`-compatible test double at the dependency boundary. The real
`langchain-core` package remains an optional integration dependency via the
`langchain` extra in `pyproject.toml`.

Run:

```bash
python -m pytest -q
```

Target: **0 skipped tests**.

## Day 20 — Passport Travel

The final integration demonstrates the complete trust pipeline:

```text
Identity → Trust → Capabilities → Tools → Security → Behavior
→ Delegation → Migration → Post-Migration Verification
→ PASSPORT TRAVEL ✓
```

Run:

```bash
python examples/day20_passport_travel.py
```

This produces `passport-travel-evidence.json`.

The dashboard also exposes the final end-to-end travel status.


## Day 19 — Web Dashboard

Agent Passport now includes a lightweight local web dashboard for demonstrations.

```text
Passport → Verification → Security → Delegation → Migration
                         ↓
                    Dashboard
```

Start it with:

```bash
python examples/day19_dashboard.py
```

Open `http://127.0.0.1:8765`.

The dashboard is intentionally dependency-free and acts as a presentation layer,
not an authentication boundary.


## Day 18 — Multi-Agent Passports

Agents can now identify peers and request scoped delegation.

```text
Agent A → Delegation Request → Agent B
                  ↓
       Capability / Tool Match
                  ↓
             ALLOW / DENY
                  ↓
        Scoped Delegation Token
```

Delegation is explicit and limited to requested capabilities/tools. It does not
automatically transfer credentials or unrestricted authority.

Run:

```bash
python examples/day18_multi_agent.py
```


## Day 17 — Behavioral Conformance

The Passport can now carry executable behavior cases and run them against an
agent implementation.

```text
Behavior Contract
      ↓
Conformance Cases
      ↓
Conformance Runner
      ↓
PASS / FAIL
```

Checks include exact output, output type, and expected failure behavior.

Run:

```bash
python examples/day17_conformance.py
```

This provides behavioral evidence in addition to identity, capability,
permission, signature, and migration checks.


## Day 16 — Security & Permission Model

Portable tools now pass through an explicit authorization check before execution.

```text
Tool Contract → Permission Policy → ALLOW / DENY → Tool Binding → Execution
```

A runtime policy can explicitly allow permissions and explicitly deny dangerous
ones. Explicit deny takes precedence.

Run:

```bash
python examples/day16_security.py
```

The policy layer is an authorization boundary, not an OS sandbox; actual
isolation remains the runtime's responsibility.

# 🪪 Agent Passport

> **Build once. Verify once. Travel anywhere.**

Agent Passport is a portable-agent architecture that separates an AI agent's
**identity, contracts, tools, model interface, and runtime** from the framework
hosting it.

## The problem

Agent implementations often become tightly coupled to their execution
framework. That makes migration expensive: identity, tools, behavior contracts,
and model integration can become framework-specific.

Agent Passport treats the portable contract as a first-class artifact.

## The idea

```text
                    Agent Passport
                         |
             +-----------+-----------+
             |           |           |
          Identity    Behavior     Tools
             |           |           |
             +-----------+-----------+
                         |
                  Portable Agent
                         |
              +----------+----------+
              |                     |
          Runtime A             Runtime B
              |                     |
              +----------+----------+
                         |
                  Verification
                         |
                 Migration PASS
```

## What the Passport contains

- Agent identity
- Capabilities
- Input/output behavior contract
- Tool contracts
- Model interface
- Compatible runtimes
- Required verification checks

A deterministic SHA-256 fingerprint identifies the Passport contents.

## Current implementation

### Core
- Portable `Agent`
- Request/response contracts
- Tool abstraction
- Runtime abstraction

### Model layer
- Provider-independent `ModelProvider`
- Deterministic mock provider
- OpenAI-compatible provider boundary

### Verification
- Schema validation
- Identity matching
- Capability checks
- Tool checks
- Behavior checks
- Runtime compatibility
- Model contract validation
- Portability checks

### Migration
- Migration manifest
- Passport fingerprint
- Source/target runtime comparison
- Identity and behavior preservation checks

### Framework interoperability
- Reference framework bridge
- Optional **real LangChain adapter** using `langchain-core`

## Quick start

```bash
pip install -e ".[dev]"
python -m pytest
python -m agent_passport.cli verify passport.yaml
python demo.py
```

For the real LangChain integration:

```bash
pip install -e ".[dev,langchain]"
python demo.py
```

## Example verification

```text
schema                 PASS
identity               PASS
behavior               PASS
tools                  PASS
runtime                PASS
```

The migration demo then compares the same agent across runtime boundaries.






## Day 15 — Portable Tools

Tools are now portable contracts rather than runtime-specific implementations.

```text
Portable Tool Contract
        ↓
 ┌──────┴──────┐
Native Binding  Framework Binding
 └──────┬──────┘
        ↓
    Same tool contract
```

Each tool declares its ID, version, input schema, output type, and permissions.
Different runtimes can bind their own implementations to that contract.

Run:

```bash
python examples/day15_tools.py
```

## Day 14 — Capability Negotiation

Migration now has a pre-flight compatibility check.

```text
Passport requirements
        ↓
Capability negotiation
        ↑
Target runtime capabilities
        ↓
COMPATIBLE ✓ / INCOMPATIBLE ✗
```

Missing capabilities and explicit policy conflicts are returned as structured
data before migration begins.

Run:

```bash
python examples/day14_negotiation.py
```

## Day 13 — Passport Versioning & Diff

Passports are now comparable across versions.

```text
Nova v1.0 → Nova v1.1
          ↓
      Passport Diff
          ↓
+ capability
+ tool
~ model
~ runtime
```

The diff engine reports additions, removals, and modifications at the exact
Passport path. This creates the foundation for approval policies before
migrating an upgraded agent.

Run:

```bash
python examples/day13_versioning.py
```

## Day 12 — Passport Registry

Passports can now be registered and discovered through a local registry.

```text
Register → Discover → Verify → Revoke
```

The registry tracks:
- Passport ID
- agent ID/name/version
- fingerprint
- issuer
- registration time
- active/revoked status
- Passport contents

Run:

```bash
python examples/day12_registry.py
```

The registry is intentionally storage-agnostic: the current implementation
uses JSON, while the same interface can later back onto SQLite or a hosted
registry.

## Day 11 — Signed Passports

The Passport can now be cryptographically signed with **Ed25519**.

This adds:

- issuer metadata
- signing timestamp
- signed content SHA-256
- signature verification
- tamper detection
- wrong-key detection

Install the optional security layer:

```bash
pip install -e ".[security]"
python examples/day11_signing.py
```

The original fingerprint remains a content identifier; the signature adds
authenticity and integrity.

## Security note

The Passport fingerprint is a content identifier, **not a digital signature**.
It does not establish issuer identity or authenticity. A future version can
add signed Passports and trust policies.

## Project structure

```text
agent-passport/
├── agent_passport/
│   ├── core/
│   ├── model/
│   ├── passport/
│   ├── verification/
│   ├── migration/
│   ├── adapters/
│   └── frameworks/
├── docs/
├── examples/
├── tests/
├── demo.py
├── passport.yaml
├── pyproject.toml
└── README.md
```

## Final demo

```bash
python demo.py
```

See `docs/demo-script.md` for a 90-second presentation script and
`SUBMISSION_CHECKLIST.md` before submitting.

## Day 22 — Cryptographic Evidence

Passport Travel evidence can now be independently verified as a cryptographic artifact. Evidence is canonicalized and SHA-256 hashed, signed with Ed25519, and bound to the exact Passport fingerprint. Verification detects both evidence tampering and attempts to present evidence for a different Passport.

Run:
```bash
python examples/day22_evidence.py
```

CLI:
```bash
agent-passport sign-evidence evidence.json passport.yaml PRIVATE_KEY ISSUER signed-evidence.json
agent-passport verify-evidence signed-evidence.json passport.yaml
```

The evidence signature proves integrity relative to the signing key; issuer trust remains a separate policy decision.

## Day 23 — Advanced Security

Delegation now supports expiring scoped tokens, replay protection, exact max-use enforcement, permission-escalation detection, purpose binding, and an auditable security event log. The reference ledger is in-memory; distributed deployments should persist consumption state transactionally.

## Day 24 — Production-Style Passport Registry

The registry now supports cryptographically verified publication and retrieval. A signed Passport can be published with its issuer public key, versions can be discovered per agent, the latest active version can be resolved, and retrieval re-checks the Passport fingerprint plus Ed25519 signature before returning the artifact.

Example:

```python
registry.publish(signed_passport, public_key=issuer_public_key)
registry.latest("nova")
registry.retrieve_verified(passport_id)
registry.revoke(passport_id)
```

CLI:

```bash
agent-passport registry register passport.json --public-key "$PUBLIC_KEY" --require-signature
agent-passport registry latest nova
agent-passport registry retrieve ap_...
agent-passport registry revoke ap_...
```

## Day 26 — Cybersecurity Hardening

The final extension adds defensive controls for hostile traffic: strict request validation, per-principal rate limiting, replay protection, secret redaction, and tamper-evident hash-chain audit logs. See `docs/cybersecurity-hardening.md` and run `python examples/day26_cybersecurity.py`.

## Day 27 — Cryptographic Key Management

Signing keys can now be stored encrypted at rest using PBKDF2-HMAC-SHA256 and
AES-256-GCM. The CLI prompts for passwords, supports safe key rotation, and
uses atomic writes with restrictive file permissions where supported.

```bash
agent-passport keystore init .agent-passport/nova.keystore.json --issuer nova
agent-passport keystore public .agent-passport/nova.keystore.json
agent-passport keystore rotate .agent-passport/nova.keystore.json
```

See `docs/day27-key-management.md`.

## Day 28 — Tool Sandboxing

- Authorization before execution
- Short-lived worker-process execution
- Timeout and resource limits
- Temporary working directory
- Output-size cap
- Fail-closed tool/binding lookup

Run:

```bash
python examples/day28_sandbox.py
```

The sandbox is defense-in-depth, not a replacement for a kernel/container sandbox for hostile code.

## Day 29 — Safe Red-Team Security Testing

The project now includes a deterministic local red-team suite that exercises
security boundaries without attacking external systems. It checks malformed
identities, oversized requests, rate-limit flooding, replay attempts,
privilege escalation, credential leakage, audit tampering, sandbox timeouts,
unauthorized tools, and evidence-chain integrity.

Run:

```bash
python examples/day29_red_team.py
```

The suite produces `red-team-report.json`. A passing red-team suite is evidence
of these implemented controls, not a claim that the system is unhackable.
Production deployments still require authenticated transport, hardened
containers/microVMs, protected secrets, persistent replay state, and independent
penetration testing.

## Day 30 — Hardened Cybersecurity Release

The final security gate combines the defensive controls from Days 26–29 into a
local release audit. It verifies zero skipped tests, safe red-team probes,
encrypted key management, tool sandboxing, request/replay/rate-limit defenses,
signed evidence, absence of private-key files and high-confidence live-secret
patterns, and required release artifacts.

Run the final audit:

```bash
python examples/day30_security_audit.py
```

The audit produces `security-audit-report.json`. Passing it is not a claim of
unhackability; hostile production code should additionally run inside hardened
containers or microVMs with least privilege and restricted network egress.

## Day 32 — Three Passport Checkpoints

The project now includes a deterministic local checkpoint runner aligned to the public submission flow shown by the challenge UI. It checks the root `agent.yaml`, the explainability document, and the Passport/evidence artifacts.

```bash
python examples/day32_checkpoints.py
```

The run produces `opengap-checkpoint-report.json` and requires all 3 local checkpoints to pass. This is a compatibility profile, not a claim about the challenge's private validator implementation.
