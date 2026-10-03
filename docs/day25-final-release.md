# Day 25 — Final Release

Day 25 packages Agent Passport as a competition-ready release rather than adding
another isolated subsystem.

## Release gate

`examples/final_release_check.py` is the single release gate. It executes:

1. the complete automated test suite;
2. Passport Travel;
3. cryptographic evidence verification;
4. advanced delegation security;
5. production-style registry verification.

The command exits non-zero if any check fails and stores the complete output in
`final-release-report.json`.

## Why this matters

The project now demonstrates a continuous trust story instead of a collection of
unrelated features:

```text
Passport → Trust → Capabilities → Tools → Security → Behavior
→ Delegation → Migration → Evidence → Registry → Audit
```

The final release deliberately keeps the dashboard as a presentation layer and
does not treat a local HTTP page as an authentication or authorization boundary.
