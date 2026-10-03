from __future__ import annotations

from typing import Any

from agent_passport.core import AgentRequest
from agent_passport.migration.runner import _stable_response


def migrate_to_framework(
    source_runtime: Any,
    framework_runtime: Any,
    request: AgentRequest,
) -> dict[str, Any]:
    source_runtime.initialize()
    try:
        source_response = source_runtime.run(request)
    finally:
        source_runtime.shutdown()

    framework_runtime.initialize()
    try:
        framework_response = framework_runtime.run(request)
    finally:
        framework_runtime.shutdown()

    source = _stable_response(source_response)
    target = _stable_response(framework_response)

    return {
        "status": (
            "PASS"
            if source["content"] == target["content"]
            and source["agent_id"] == target["agent_id"]
            else "FAIL"
        ),
        "source_runtime": source_runtime.runtime_name,
        "target_runtime": framework_runtime.runtime_name,
        "identity_preserved": source["agent_id"] == target["agent_id"],
        "behavior_preserved": source["content"] == target["content"],
        "source": source,
        "target": target,
    }
