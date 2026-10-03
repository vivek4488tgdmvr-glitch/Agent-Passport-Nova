# Behavioral Conformance — Day 17

A Passport should not rely only on self-declared behavior. Day 17 adds
executable conformance cases that can be run against an agent implementation.

```text
Passport Behavior Contract
          |
    Test Cases
          |
   Conformance Runner
          |
    +-----+-----+
    |           |
  PASS         FAIL
    |           |
  Evidence    Migration blocked
```

## Test case types

A case can check:

- exact output equality
- output type
- expected exceptions

Example:

```python
BehaviorCase(
    name="structured-output",
    input="hello",
    expected_output={"echo": "hello"},
)
```

## Why this matters

Identity says *which agent this is*.
Capabilities say *what it can provide*.
Security says *what it is allowed to do*.
Behavioral conformance adds evidence for *how it actually behaves*.

Conformance is intentionally deterministic in this first implementation.
For stochastic LLM behavior, production systems can later add schemas,
tolerances, evaluators, golden datasets, and repeated-trial policies.
