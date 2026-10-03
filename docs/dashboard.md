# Agent Passport Dashboard — Day 19

Day 19 adds a dependency-free local web dashboard for demonstrations.

## Start

```bash
python examples/day19_dashboard.py
```

Then open:

`http://127.0.0.1:8765`

The dashboard exposes:

- agent identity
- Passport version and fingerprint
- signature/registry status
- capabilities
- portable tools
- runtime compatibility
- security policy
- multi-agent delegation
- migration verification
- the complete trust pipeline

A JSON endpoint is also available at `/api/passport`.

The dashboard is a local presentation layer. It is not itself an
authentication boundary and should not be exposed publicly without an
appropriate production server and access control.
