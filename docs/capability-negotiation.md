# Capability Negotiation — Day 14

Migration now has a pre-flight compatibility step.

```text
              Passport
                 |
          required capabilities
                 |
                 v
          CAPABILITY CHECK
                 ^
                 |
          runtime capabilities
                 |
              Runtime
```

## Decision

A target is compatible when every Passport-required capability is provided
and there are no declared policy conflicts.

```text
required ⊆ provided
        AND
conflicts = empty
```

## Example

```text
Passport requires:
✓ reasoning
✓ structured_output
✓ tool_use
✓ web_search

Runtime provides:
✓ reasoning
✓ structured_output

Result:
INCOMPATIBLE

Missing:
✗ tool_use
✗ web_search
```

## Why this changes migration

The migration runner can perform negotiation before transferring an agent.
A failed negotiation gives the operator a machine-readable reason instead
of allowing a partially compatible runtime to fail later.

This is a policy layer, not a claim that every runtime capability can be
objectively measured. Runtime adapters must declare their supported
capabilities.
