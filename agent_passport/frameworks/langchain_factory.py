from __future__ import annotations

from agent_passport.core import Agent, AgentRequest


def build_langchain_runnable(agent: Agent):
    """Build a real LangChain RunnableLambda around the portable agent.

    Import is intentionally local: users who do not need LangChain do not
    need the optional dependency.
    """
    try:
        from langchain_core.runnables import RunnableLambda
    except ImportError as exc:
        raise RuntimeError(
            "LangChain integration requires: pip install langchain-core"
        ) from exc

    def invoke(message: str) -> str:
        response = agent.handle(AgentRequest(message))
        return response.content

    return RunnableLambda(invoke)
