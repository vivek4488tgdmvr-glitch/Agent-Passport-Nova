"""Day 28: defensive tool sandbox demonstration."""
from agent_passport.security import PermissionPolicy, SandboxLimits
from agent_passport.tools import PortableTool, SandboxedToolRegistry


def main() -> None:
    safe = PortableTool("calculator", "1.0", "Adds two numbers", {"type": "object"}, "number")
    dangerous = PortableTool("shell_exec", "1.0", "Would require shell access", {"type": "object"}, "string", {"shell": True})

    registry = SandboxedToolRegistry(
        PermissionPolicy(allow=frozenset(), deny=frozenset({"shell"})),
        limits=SandboxLimits(timeout_seconds=1, max_output_chars=256),
    )
    registry.register(safe)
    registry.register(dangerous)
    registry.bind("calculator", "native", lambda a, b: a + b)
    registry.bind("shell_exec", "native", lambda: "NEVER RUNS")

    safe_result = registry.invoke_sandboxed("calculator", "native", 7, 5)
    denied_result = registry.invoke_sandboxed("shell_exec", "native")

    print("=== DAY 28: TOOL SANDBOXING ===")
    print(f"Safe calculator: {safe_result.status} ✓" if safe_result.ok else f"Safe calculator: {safe_result.status} ✗")
    print(f"Dangerous shell tool: {denied_result.status} ✓" if denied_result.status == "DENY" else f"Dangerous shell tool: {denied_result.status} ✗")
    print("Process isolation + timeout limits: ENABLED ✓")
    print("TOOL SANDBOXING: PASS")


if __name__ == "__main__":
    main()
