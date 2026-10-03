"""Framework-neutral portable tool contracts."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class PortableTool:
    tool_id: str
    version: str
    description: str
    input_schema: dict[str, Any]
    output_type: str
    permissions: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.tool_id,
            "version": self.version,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_type": self.output_type,
            "permissions": self.permissions,
        }


@dataclass
class ToolBinding:
    tool: PortableTool
    runtime: str
    handler: Callable[..., Any]

    def invoke(self, *args, **kwargs) -> Any:
        return self.handler(*args, **kwargs)


def validate_tool_contract(tool: PortableTool) -> dict[str, Any]:
    errors = []
    if not tool.tool_id:
        errors.append("tool_id is required")
    if not tool.version:
        errors.append("version is required")
    if not isinstance(tool.input_schema, dict):
        errors.append("input_schema must be an object")
    if not tool.output_type:
        errors.append("output_type is required")

    allowed_permissions = {"network", "filesystem_read", "filesystem_write", "shell"}
    unknown = set(tool.permissions) - allowed_permissions
    if unknown:
        errors.append(f"unknown permissions: {sorted(unknown)}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "tool_id": tool.tool_id,
        "version": tool.version,
    }
