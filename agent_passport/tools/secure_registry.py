from __future__ import annotations

from typing import Any

from .registry import ToolRegistry
from ..security import PermissionPolicy, SecurityEngine


class SecureToolRegistry(ToolRegistry):
    """Tool registry that checks declared tool permissions before invocation."""

    def __init__(self, policy: PermissionPolicy):
        super().__init__()
        self.security = SecurityEngine(policy)

    def invoke(self, tool_id: str, runtime: str, *args, **kwargs) -> Any:
        tool = self.get(tool_id)
        if tool is None:
            raise KeyError(f"Unknown portable tool: {tool_id}")

        requested = {
            permission
            for permission, enabled in tool.permissions.items()
            if enabled
        }
        self.security.require(requested)
        return super().invoke(tool_id, runtime, *args, **kwargs)
