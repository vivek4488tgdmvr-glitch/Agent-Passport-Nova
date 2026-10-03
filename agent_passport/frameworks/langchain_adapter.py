from __future__ import annotations

from typing import Any

from agent_passport.core import AgentRequest, AgentResponse


class LangChainAdapter:
    """Optional LangChain integration.

    LangChain is imported lazily so Agent Passport's core remains usable
    without installing a framework. The adapter expects a LangChain Runnable
    (for example a RunnableLambda or a composed LCEL chain) exposing invoke().
    """

    runtime_name = "langchain"

    def __init__(self, runnable: Any, passport_agent_id: str):
        if not hasattr(runnable, "invoke"):
            raise TypeError("LangChain runnable must expose invoke().")
        self.runnable = runnable
        self.passport_agent_id = passport_agent_id
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True

    def run(self, request: AgentRequest) -> AgentResponse:
        if not self.initialized:
            raise RuntimeError("LangChain adapter is not initialized.")

        result = self.runnable.invoke(request.message)

        if isinstance(result, str):
            content = result
        elif hasattr(result, "content"):
            content = str(result.content)
        else:
            content = str(result)

        return AgentResponse(
            content=content,
            metadata={
                "agent_id": self.passport_agent_id,
                "framework": self.runtime_name,
            },
        )

    def shutdown(self) -> None:
        self.initialized = False
