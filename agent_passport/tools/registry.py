from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contract import PortableTool, ToolBinding


class ToolRegistry:
    """Runtime-neutral tool registry with explicit bindings."""

    def __init__(self):
        self._tools: dict[str, PortableTool] = {}
        self._bindings: dict[tuple[str, str], ToolBinding] = {}

    def register(self, tool: PortableTool) -> PortableTool:
        self._tools[tool.tool_id] = tool
        return tool

    def get(self, tool_id: str) -> PortableTool | None:
        return self._tools.get(tool_id)

    def bind(
        self,
        tool_id: str,
        runtime: str,
        handler,
    ) -> ToolBinding:
        tool = self.get(tool_id)
        if tool is None:
            raise KeyError(f"Unknown portable tool: {tool_id}")
        binding = ToolBinding(tool, runtime, handler)
        self._bindings[(tool_id, runtime)] = binding
        return binding

    def binding(self, tool_id: str, runtime: str) -> ToolBinding | None:
        return self._bindings.get((tool_id, runtime))

    def invoke(self, tool_id: str, runtime: str, *args, **kwargs) -> Any:
        binding = self.binding(tool_id, runtime)
        if binding is None:
            raise RuntimeError(
                f"No binding for tool '{tool_id}' on runtime '{runtime}'"
            )
        return binding.invoke(*args, **kwargs)

    def portable_tools(self) -> list[PortableTool]:
        return sorted(self._tools.values(), key=lambda x: x.tool_id)

    def runtimes_for(self, tool_id: str) -> list[str]:
        return sorted(
            runtime for (tid, runtime) in self._bindings if tid == tool_id
        )
