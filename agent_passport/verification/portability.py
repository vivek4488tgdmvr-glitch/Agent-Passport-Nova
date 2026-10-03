from __future__ import annotations

from typing import Any

from agent_passport.core import Agent, AgentRequest


def compare_runtimes(
    agent: Agent,
    runtimes: list[Any],
    request: AgentRequest,
) -> dict[str, Any]:
    """Run the same request through each runtime and compare stable outputs."""

    results = []
    for runtime in runtimes:
        runtime.initialize()
        try:
            response = runtime.run(request)
            results.append({
                "runtime": runtime.runtime_name,
                "status": "PASS",
                "content": response.content,
                "agent_id": response.metadata.get("agent_id"),
            })
        except Exception as exc:
            results.append({
                "runtime": runtime.runtime_name,
                "status": "FAIL",
                "error": str(exc),
            })
        finally:
            runtime.shutdown()

    successful = [r for r in results if r["status"] == "PASS"]
    contents = {r["content"] for r in successful}
    identities = {r["agent_id"] for r in successful}

    portable = (
        len(successful) == len(runtimes)
        and len(contents) == 1
        and identities == {agent.agent_id}
    )

    return {
        "status": "PASS" if portable else "FAIL",
        "portable": portable,
        "results": results,
    }
