# Trust-Boundary Security Matrix — Day 40

| Boundary | Adversarial condition | Expected result |
|---|---|---|
| Passport | Modified signed content | Reject |
| Registry | Revoked Passport retrieval | Reject |
| Delegation | Expired token | Reject |
| Delegation | Replay same token/use | Reject |
| Authorization | Capability escalation | Reject |
| Tools | Unauthorized tool invocation | Reject |
| Sandbox | Execution timeout | Terminate |
| Evidence | Modified evidence | Reject |
| Audit | Modified prior audit event | Integrity failure |
| Dashboard | Untrusted rendered value | Safe text rendering |
| Model endpoint | Untrusted endpoint configuration | Deployment policy must reject/allowlist |
| Secrets | Credential-like values in audit | Redact |

These are local defensive validation cases. They do not target external systems.
