# Architecture

```text
                         AGENT PASSPORT
                               |
             +-----------------+-----------------+
             |                 |                 |
          Identity          Contracts          Tools
             |                 |                 |
             +-----------------+-----------------+
                               |
                        Portable Agent Core
                               |
                    +----------+----------+
                    |                     |
              ModelProvider          Runtime Contract
                    |                     |
          +---------+--------+      +-----+------+
          |                  |      |            |
        Mock       OpenAI-Compatible Native   Framework
          |                  |      |            |
          +---------+--------+      +-----+------+
                    |                     |
                    +----------+----------+
                               |
                       Verification Engine
                               |
                 +-------------+-------------+
                 |             |             |
              Identity      Behavior     Portability
                 |             |             |
                 +-------------+-------------+
                               |
                         Migration Report
```

## Core principle

Framework-specific code stays at the edges.

The Passport, contracts, verification, and portable agent core do not need
to know which framework hosts the agent.

## Passport as an artifact

A Passport captures:

- agent identity
- capabilities
- input/output behavior
- tool contracts
- model interface
- compatible runtimes
- required verification checks

Its deterministic fingerprint provides a stable content identifier.

## Migration

Migration does not copy framework internals. It preserves the portable
contract and executes the same agent through a different runtime adapter.

The verification engine then checks the properties that are required to remain
stable.
