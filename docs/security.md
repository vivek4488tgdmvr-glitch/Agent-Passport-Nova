# Security & Permission Model — Day 16

Day 16 adds a policy enforcement layer between a portable tool contract and
runtime execution.

```text
Portable Tool
      |
   permissions
      |
Security Policy
      |
   ALLOW / DENY
      |
   Tool Binding
      |
   Execution
```

## Policy semantics

A permission is executable only when:

1. it is explicitly allowed by the runtime policy, and
2. it is not explicitly denied.

Explicit deny takes precedence over allow.

## Example

```python
PermissionPolicy(
    allow=frozenset({"network"}),
    deny=frozenset({"shell", "filesystem_write"}),
)
```

A tool declaring `network: true` can execute. A tool declaring `shell: true`
is blocked before its handler is called.

## Important security boundary

The policy engine is an authorization decision point, not a sandbox.
Actual OS/container/network isolation must be implemented by the runtime.

## Threat model addressed

This layer helps prevent accidental execution of a tool whose declared
permissions exceed the runtime's granted policy. It does not claim to
defend against a compromised runtime, malicious native code, or a forged
policy source.
