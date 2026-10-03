# Portable Tools — Day 15

Agent portability is incomplete if tools remain framework-specific.

Day 15 introduces a framework-neutral tool contract:

```text
                  Portable Tool
                       |
            +----------+----------+
            |                     |
         Native               Framework
         Binding               Binding
            |                     |
            +----------+----------+
                       |
                   Tool result
```

## Portable contract

A tool declares:

- stable tool ID
- tool version
- description
- input schema
- output type
- permissions

Runtime-specific implementations are bindings. The Passport can describe
the tool without embedding a particular framework's tool object.

## Security

Permissions are declarative. They do not magically sandbox a process.
Runtime adapters must enforce the declared permissions.

## Why this matters

When an agent moves from Runtime A to Runtime B, the destination only needs
to provide a binding that satisfies the same portable tool contract.
