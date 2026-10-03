# Day 23 — Advanced Delegation Security

Delegation tokens are now enforced as scoped capabilities rather than simple data objects.

## Controls

- **Expiration:** tokens may carry an absolute UTC expiry.
- **Replay protection:** every token has a unique ID and the engine tracks consumed uses.
- **Max-use enforcement:** a token cannot be consumed more than `max_uses` times.
- **Permission-escalation detection:** a request cannot ask for capabilities or tools outside the token's original scope.
- **Purpose binding:** a non-empty purpose on the token must match the consuming request.
- **Audit log:** issuance, successful consumption, and denials are recorded with token ID, principals, reason, and timestamp.

The current ledger is intentionally in-memory. Production deployments should persist the token-use state in a transactional store when replay protection must survive process restarts or operate across multiple verifier instances.
