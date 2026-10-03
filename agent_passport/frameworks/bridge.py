from __future__ import annotations

from agent_passport.core import Agent, AgentRequest, AgentResponse
from agent_passport.frameworks.external import ExternalFrameworkAdapter, FrameworkAgent


def bridge_agent(agent: Agent) -> ExternalFrameworkAdapter:
    """Convert the portable Agent contract into a framework-hosted agent."""

    def handler(message: str) -> str:
        response = agent.handle(AgentRequest(message))
        return response.content

    framework_agent = FrameworkAgent(
        name=agent.name,
        instructions="Hosted through an external framework adapter.",
        handler=handler,
        metadata={"source": "agent-passport"},
    )

    return ExternalFrameworkAdapter(
        framework_agent=framework_agent,
        passport_agent_id=agent.agent_id,
    )
