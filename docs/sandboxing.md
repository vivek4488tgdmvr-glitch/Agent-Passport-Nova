# Day 28 — Tool Sandboxing

Agent Passport now has a defensive tool-execution boundary.

## Controls

1. **Authorization before execution** — the tool's declared permissions are evaluated against an explicit allow/deny policy. Deny wins.
2. **Short-lived worker process** — approved handlers run in a separate process rather than inside the caller process.
3. **Timeout enforcement** — a worker that exceeds the configured time is killed.
4. **Resource limits** — on POSIX systems, CPU, address-space and file-size limits are applied where the OS exposes them.
5. **Temporary working directory** — the worker starts in an isolated temporary directory which is deleted after execution.
6. **Output cap** — large textual results are truncated before being returned.
7. **Fail-closed binding lookup** — missing tools/bindings do not execute anything.

## Important security boundary

This is **defense in depth, not a claim of a complete OS sandbox**. A Python callable running in the same host kernel can still have capabilities that a kernel/container policy does not explicitly remove. For hostile third-party code, use a dedicated sandbox such as a locked-down container or microVM with a read-only filesystem, seccomp/AppArmor/SELinux policy, dropped privileges, no host mounts, and controlled egress.

The Passport layer should therefore authorize the tool first and then hand execution to the deployment's stronger isolation layer.
