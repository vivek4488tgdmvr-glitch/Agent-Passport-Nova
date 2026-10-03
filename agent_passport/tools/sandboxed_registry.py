from __future__ import annotations

from typing import Any

from .registry import ToolRegistry
from ..security import PermissionPolicy
from ..security.sandbox import SandboxLimits, SandboxResult, ToolSandbox


class SandboxedToolRegistry(ToolRegistry):
    """Tool registry that requires authorization and bounded process execution."""

    def __init__(self, policy: PermissionPolicy, *, limits: SandboxLimits | None = None):
        super().__init__()
        self.sandbox = ToolSandbox(policy, limits=limits)

    def invoke_sandboxed(self, tool_id: str, runtime: str, *args, **kwargs) -> SandboxResult:
        tool = self.get(tool_id)
        if tool is None:
            return SandboxResult("DENY", error=f"Unknown portable tool: {tool_id}")
        binding = self.binding(tool_id, runtime)
        if binding is None:
            return SandboxResult("DENY", error=f"No binding for tool '{tool_id}' on runtime '{runtime}'")
        requested = {p for p, enabled in tool.permissions.items() if enabled}
        return self.sandbox.execute(binding.handler, requested, *args, **kwargs)
