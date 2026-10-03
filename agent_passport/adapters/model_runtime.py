from __future__ import annotations

from agent_passport.core.llm_agent import LLMBackedAgent
from agent_passport.core.contracts import AgentRequest, AgentResponse


class ModelRuntime:
    """Runtime adapter that exposes an LLM-backed agent through our contract."""

    runtime_name = "model-runtime"

    def __init__(self, agent: LLMBackedAgent):
        self.agent = agent
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True

    def run(self, request: AgentRequest) -> AgentResponse:
        if not self.initialized:
            raise RuntimeError("Runtime must be initialized before run().")

        result = self.agent.run(request.message)
        return AgentResponse(
            content=result.content,
            metadata={
                "agent_id": self.agent.agent_id,
                "agent_version": self.agent.version,
                "provider": result.provider,
                "model": result.model,
            },
        )

    def shutdown(self) -> None:
        self.initialized = False
