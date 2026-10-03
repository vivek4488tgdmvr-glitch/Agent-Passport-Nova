# 90-second demo script

**0–15 sec — Problem**

"AI agents are increasingly tied to the runtime or framework they were built
with. Moving one can mean rebuilding identity, tools, and contracts."

**15–30 sec — Passport**

"This project introduces an Agent Passport: a machine-readable identity and
contract for an agent."

Show `passport.yaml`.

**30–45 sec — Verify**

Run:

```bash
python -m agent_passport.cli verify passport.yaml
```

Say:

"The verifier checks identity, behavior, tools, and runtime compatibility."

**45–65 sec — Travel**

Run:

```bash
python demo.py
```

Show the same Nova agent going from the native runtime through the framework
adapter.

**65–80 sec — Proof**

Point to:

- same agent ID
- same Passport fingerprint
- identity preserved
- behavior preserved
- migration PASS

**80–90 sec — Close**

"The key idea is simple: build the agent once, describe its contract once,
verify it, and make the runtime an adapter rather than the agent's identity."
