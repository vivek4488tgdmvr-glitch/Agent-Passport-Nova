from agent_passport.core import Agent, AgentRequest, AgentResponse


class MockFrameworkRuntime:
    """A second runtime-shaped adapter for Day 2 portability testing.

    It intentionally has a different internal lifecycle while exposing the
    same public runtime contract as the native adapter.
    """

    runtime_name = "mock-framework"

    def __init__(self, agent: Agent):
        self.agent = agent
        self.state = "created"

    def initialize(self) -> None:
        self.state = "ready"

    def run(self, request: AgentRequest) -> AgentResponse:
        if self.state != "ready":
            raise RuntimeError("Mock framework is not ready.")
        response = self.agent.handle(request)
        response.metadata["runtime"] = self.runtime_name
        return response

    def shutdown(self) -> None:
        self.state = "stopped"
