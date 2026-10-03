# Passport Registry — Day 12

The registry turns individual Passport files into discoverable, version-aware
records.

```text
                   Passport Registry
                          |
         +----------------+----------------+
         |                |                |
       Nova            Nova           Researcher
        v1.0             v1.1              v2.0
         |                |                |
      ACTIVE           ACTIVE            ACTIVE
                          |
                     fingerprint
                          |
                     verification
```

## Operations

- Register a Passport
- List active Passports
- Inspect a Passport record
- Find an agent's versions
- Verify registered content
- Revoke a Passport

## Trust model

Registration does not automatically make an issuer trusted. The registry
records issuer metadata when available. Signed Passports from Day 11 can be
combined with an issuer trust policy in a later stage.

Revocation is a registry state change. A revoked Passport remains in the
registry for auditability but is excluded from the default active listing.

## Storage

The reference implementation uses a small JSON file-backed store so the
concept can later be replaced by SQLite, PostgreSQL, or a hosted registry
without changing the Passport contract.
