from __future__ import annotations

from typing import Any

from agent_passport.core import AgentRequest


def _stable_response(response: Any) -> dict[str, Any]:
    return {
        "content": response.content,
        "agent_id": response.metadata.get("agent_id"),
        "provider": response.metadata.get("provider"),
        "model": response.metadata.get("model"),
    }


def migrate_agent(
    source_runtime: Any,
    target_runtime: Any,
    request: AgentRequest,
) -> dict[str, Any]:
    """Execute one agent through source and target runtimes.

    The agent object is intentionally unchanged; only the runtime wrapper
    changes. This is the core migration proof used by the demo.
    """
    source_runtime.initialize()
    try:
        source_response = source_runtime.run(request)
    finally:
        source_runtime.shutdown()

    target_runtime.initialize()
    try:
        target_response = target_runtime.run(request)
    finally:
        target_runtime.shutdown()

    source = _stable_response(source_response)
    target = _stable_response(target_response)

    stable_fields = ["content", "agent_id", "provider", "model"]
    differences = {
        field: {"source": source[field], "target": target[field]}
        for field in stable_fields
        if source[field] != target[field]
    }

    return {
        "status": "PASS" if not differences else "FAIL",
        "source_runtime": source_runtime.runtime_name,
        "target_runtime": target_runtime.runtime_name,
        "same_agent_identity": source["agent_id"] == target["agent_id"],
        "same_content": source["content"] == target["content"],
        "differences": differences,
        "source": source,
        "target": target,
    }


def verify_migration(
    manifest,
    migration_result: dict[str, Any],
) -> dict[str, Any]:
    checks = {
        "manifest_identity": bool(manifest.agent_id),
        "source_runtime": bool(manifest.source_runtime),
        "target_runtime": bool(manifest.target_runtime),
        "runtime_result": migration_result["status"] == "PASS",
        "identity_preserved": migration_result["same_agent_identity"],
    }

    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "manifest": manifest.to_dict(),
    }
