# Multi-Agent Passports & Delegation — Day 18

Multiple agents can now participate in a scoped delegation protocol.

```text
Agent A Passport
      |
   Request
      |
Delegation Engine
      |
   Agent B Passport
      |
  capability/tool match
      |
   ALLOW / DENY
      |
Scoped Delegation Token
```

## Agent peer record

A peer record contains:

- agent ID and version
- declared capabilities
- declared tools
- optional issuer
- optional Passport fingerprint

## Delegation scope

A request explicitly states:

- requester
- target
- required capabilities
- required tools
- purpose
- maximum uses

The target must satisfy the requested capability and tool scope.

## Security boundary

A delegation token is intentionally narrow. It does not contain API keys,
passwords, or other credentials. It only describes the authorized scope.

This implementation is a local protocol reference. Production deployments
should bind delegation to signed Passports, authenticated channels,
expiration, replay protection, and runtime-enforced credentials.
