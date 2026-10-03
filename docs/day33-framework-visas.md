# Day 33 — Framework Visas

Day 33 adds the OpenGAP-facing framework visa boundary for the four framework
entries shown by the public challenge UI: OpenAI SDK, CrewAI, Claude Code, and
Lyzr.

## What a visa means here

A visa is a deterministic compatibility/export record issued only after the
local adapter has produced an internally consistent framework-shaped artifact.
It binds the target framework to the Passport agent id and version.

These adapters are **compatibility contracts**, not claims that the corresponding
third-party SDKs are installed or that these artifacts are official SDK exports.
Real framework integrations can be layered on the same boundary when their SDKs
and challenge-specific contracts are available.

## Four targets

| Target | Adapter | Artifact entrypoint |
|---|---|---|
| OpenAI SDK | `OpenAISDKVisaAdapter` | `responses` |
| CrewAI | `CrewAIVisaAdapter` | `agent` |
| Claude Code | `ClaudeCodeVisaAdapter` | `agent` |
| Lyzr | `LyzrVisaAdapter` | `agent` |

## Verification

```python
from agent_passport.visas import export_all_visas, verify_export

exports = export_all_visas(agent)
assert all(verify_export(item) for item in exports.values())
```

The implementation deliberately does not store API keys, passwords, or other
credentials in visa artifacts.
