# Passport Versioning & Diff — Day 13

Every Passport version is an auditable contract.

```text
Nova v1.0
    |
    | upgrade
    v
Nova v1.1
    |
    v
Passport Diff
```

The diff engine reports changes at the actual Passport path.

## Change types

`+` Added — a new capability, tool, runtime, or field.

`-` Removed — something present in the previous Passport disappeared.

`~` Modified — an existing value changed.

## Example

```text
+ identity.capabilities[]
    value: "web_search"

+ tools[]
    value: {"name": "web_search", ...}

~ model.model
    before: "any"
    after: "new-model"
```

## Why this matters

Migration should not silently move a materially different agent.

A future migration policy can use this diff to require approval when:
- permissions change
- capabilities are added
- tools are added or removed
- model behavior changes
- runtime compatibility changes

The registry from Day 12 can store multiple versions, while this engine
explains what changed between them.
