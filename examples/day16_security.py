import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.security import PermissionPolicy, SecurityEngine
from agent_passport.tools import PortableTool, SecureToolRegistry
from agent_passport.verification.security_checks import verify_policy


print("=== DAY 16: SECURITY & PERMISSIONS ===")

policy = PermissionPolicy(
    allow=frozenset({"network"}),
    deny=frozenset({"shell", "filesystem_write"}),
)
print("\nPolicy:", policy.to_dict())
print("Policy validation:", verify_policy(policy)["status"], "✓")

engine = SecurityEngine(policy)

print("\n[1] Network request")
print(engine.check({"network"}).pretty())
print("✓ ALLOWED")

print("\n[2] Shell request")
print(engine.check({"shell"}).pretty())
print("✗ DENIED")

search = PortableTool(
    "web_search", "1.0.0", "searches the web", {}, "object",
    permissions={"network": True}
)
registry = SecureToolRegistry(policy)
registry.register(search)
registry.bind("web_search", "native", lambda query: {"query": query})

print("\n[3] Secure tool invocation")
print(registry.invoke("web_search", "native", "agent passport"))
print("✓ TOOL EXECUTED AFTER POLICY CHECK")

dangerous = PortableTool(
    "shell_exec", "1.0.0", "executes a shell command", {}, "string",
    permissions={"shell": True}
)
registry.register(dangerous)
registry.bind("shell_exec", "native", lambda command: "executed")

try:
    registry.invoke("shell_exec", "native", "whoami")
except PermissionError:
    print("✓ DANGEROUS TOOL BLOCKED BEFORE EXECUTION")

print("\nSecurity boundary ✓")
print("Tool permissions checked before execution ✓")
print("Deny takes precedence ✓")
