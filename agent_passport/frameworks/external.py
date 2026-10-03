from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agent_passport.core import AgentRequest, AgentResponse


@dataclass
class FrameworkAgent:
    """Small framework-shaped object representing an external host.

    This is intentionally an adapter boundary, not a claim that this class
    is an official implementation of any named third-party framework.
    """

    name: str
    instructions: str
    handler: Callable[[str], str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def invoke(self, message: str) -> str:
        return self.handler(message)


class ExternalFrameworkAdapter:
    """Adapts a framework-native agent to the Agent Passport runtime contract."""

    runtime_name = "external-framework"

    def __init__(self, framework_agent: FrameworkAgent, passport_agent_id: str):
        self.framework_agent = framework_agent
        self.passport_agent_id = passport_agent_id
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True

    def run(self, request: AgentRequest) -> AgentResponse:
        if not self.initialized:
            raise RuntimeError("External framework adapter is not initialized.")

        content = self.framework_agent.invoke(request.message)

        return AgentResponse(
            content=content,
            metadata={
                "agent_id": self.passport_agent_id,
                "framework": self.runtime_name,
                **self.framework_agent.metadata,
            },
        )

    def shutdown(self) -> None:
        self.initialized = False
