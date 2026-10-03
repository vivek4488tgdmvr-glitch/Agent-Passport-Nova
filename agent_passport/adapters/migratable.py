from __future__ import annotations

from agent_passport.core import Agent, AgentRequest, AgentResponse


class MigratableRuntime:
    """Generic runtime adapter used to model a second independent host.

    Its internal lifecycle differs from NativeRuntime, but the external
    runtime contract remains identical.
    """

    runtime_name = "portable-host"

    def __init__(self, agent: Agent):
        self.agent = agent
        self.lifecycle = "created"

    def initialize(self) -> None:
        self.lifecycle = "running"

    def run(self, request: AgentRequest) -> AgentResponse:
        if self.lifecycle != "running":
            raise RuntimeError("Portable host is not running.")

        response = self.agent.handle(request)
        response.metadata["runtime"] = self.runtime_name
        return response

    def shutdown(self) -> None:
        self.lifecycle = "stopped"
