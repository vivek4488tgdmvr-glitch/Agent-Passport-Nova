from agent_passport.core import Agent, AgentRequest, AgentResponse


class NativeRuntime:
    """Reference runtime used as the portability baseline."""

    runtime_name = "native"

    def __init__(self, agent: Agent):
        self.agent = agent
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True

    def run(self, request: AgentRequest) -> AgentResponse:
        if not self.initialized:
            raise RuntimeError("Runtime must be initialized before run().")
        return self.agent.handle(request)

    def shutdown(self) -> None:
        self.initialized = False
