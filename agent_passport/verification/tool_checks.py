from __future__ import annotations

from typing import Iterable
from ..tools.contract import PortableTool, validate_tool_contract


def verify_portable_tools(tools: Iterable[PortableTool]) -> dict:
    reports = [validate_tool_contract(tool) for tool in tools]
    failed = [r for r in reports if r["status"] != "PASS"]
    return {
        "status": "PASS" if not failed else "FAIL",
        "tools": reports,
    }
