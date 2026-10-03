# Passport Travel — Day 20

Day 20 is the end-to-end demonstration of the Agent Passport architecture.

```text
Identity
   ↓
Passport Trust
   ↓
Capability Negotiation
   ↓
Portable Tools
   ↓
Security Policy
   ↓
Behavioral Conformance
   ↓
Multi-Agent Delegation
   ↓
Runtime Migration
   ↓
Post-Migration Verification
   ↓
PASSPORT TRAVEL ✓
```

Run:

```bash
python examples/day20_passport_travel.py
```

The demo creates a structured evidence report and writes
`passport-travel-evidence.json`.

## Judge story

The agent does not merely carry an identity document. Before and after
travel, the system checks the properties that matter for trust:

- who the agent is
- whether its Passport is trusted
- whether the destination supports its capabilities
- whether its tools have portable contracts
- whether requested actions satisfy security policy
- whether its behavior conforms
- whether delegation stays within scope
- whether identity and behavior remain valid after migration

The dashboard exposes the same story visually.
