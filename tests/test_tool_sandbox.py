import time

from agent_passport.security import PermissionPolicy, SandboxLimits, ToolSandbox
from agent_passport.tools import PortableTool, SandboxedToolRegistry


def test_sandbox_executes_authorized_tool_in_child():
    sandbox = ToolSandbox(PermissionPolicy(allow=frozenset()), limits=SandboxLimits(timeout_seconds=1))
    result = sandbox.execute(lambda a, b: a + b, set(), 2, 3)
    assert result.ok
    assert result.value == 5


def test_sandbox_denies_unapproved_permission_before_execution():
    called = []
    sandbox = ToolSandbox(PermissionPolicy(allow=frozenset()), limits=SandboxLimits(timeout_seconds=1))
    result = sandbox.execute(lambda: called.append(True), {"shell"})
    assert result.status == "DENY"
    assert called == []


def test_sandbox_kills_timed_out_handler():
    sandbox = ToolSandbox(PermissionPolicy(allow=frozenset()), limits=SandboxLimits(timeout_seconds=0.1))
    result = sandbox.execute(lambda: time.sleep(2), set())
    assert result.status == "TIMEOUT"


def test_sandbox_truncates_large_text_output():
    sandbox = ToolSandbox(PermissionPolicy(allow=frozenset()), limits=SandboxLimits(max_output_chars=32, timeout_seconds=1))
    result = sandbox.execute(lambda: "x" * 1000, set())
    assert result.ok
    assert result.output_truncated
    assert len(result.value) <= 32


def test_sandboxed_registry_enforces_tool_permissions_and_binding():
    tool = PortableTool("calculator", "1.0", "adds", {"type": "object"}, "number")
    registry = SandboxedToolRegistry(PermissionPolicy(allow=frozenset()), limits=SandboxLimits(timeout_seconds=1))
    registry.register(tool)
    registry.bind("calculator", "native", lambda a, b: a + b)
    result = registry.invoke_sandboxed("calculator", "native", 4, 6)
    assert result.ok and result.value == 10
