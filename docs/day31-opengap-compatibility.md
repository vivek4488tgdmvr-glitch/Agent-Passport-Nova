# Day 31 — OpenGAP Compatibility

Day 31 adds a challenge-facing compatibility boundary without replacing the
existing Agent Passport format.

## Why two files?

- `passport.yaml` remains the full Agent Passport source of truth.
- root `agent.yaml` is the strict OpenGAP-facing compatibility document.

This separation lets the project preserve its richer internal contract while
presenting a small, deterministic entrypoint to a validator.

## Profile

The repository targets the `0.1.0` OpenGAP profile visible in the challenge UI.
The local validator enforces:

- root-level `agent.yaml`
- exact `spec: 0.1.0`
- agent identity fields
- behavior input/output contracts
- tool contracts
- framework export targets
- security declarations
- rejection of unknown root fields

The local profile is intentionally documented as a compatibility layer, not as
a claim that it duplicates the private HiDevs validator.

## Commands

```bash
python examples/day31_opengap.py
python -m pytest -q
```

## Framework targets

The compatibility document records the four framework visa targets visible in
the challenge UI: OpenAI SDK, CrewAI, Claude Code, and Lyzr. Day 33 will add
and test the actual export adapters for those targets.
