from dataclasses import dataclass, field
from typing import Any, Callable

from .contracts import AgentRequest, AgentResponse


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]
    input_schema: dict[str, Any] = field(default_factory=dict)
    output_type: str = "json"

    def execute(self, **kwargs: Any) -> Any:
        return self.function(**kwargs)

    def contract(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_type": self.output_type,
        }


@dataclass
class Agent:
    agent_id: str
    name: str
    version: str
    capabilities: list[str] = field(default_factory=list)
    tools: dict[str, Tool] = field(default_factory=dict)

    def describe(self) -> dict[str, Any]:
        return {
            "id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities,
            "tools": sorted(self.tools.keys()),
        }

    def register_tool(
        self,
        name: str,
        function: Callable[..., Any],
        description: str = "",
        input_schema: dict[str, Any] | None = None,
        output_type: str = "json",
    ) -> None:
        if not name.strip():
            raise ValueError("Tool name cannot be empty.")

        self.tools[name] = Tool(
            name=name,
            description=description,
            function=function,
            input_schema=input_schema or {},
            output_type=output_type,
        )

    def execute_tool(self, name: str, **kwargs: Any) -> Any:
        if name not in self.tools:
            raise KeyError(f"Unknown tool: {name}")
        return self.tools[name].execute(**kwargs)

    def tool_contracts(self) -> list[dict[str, Any]]:
        return [tool.contract() for tool in self.tools.values()]

    def handle(self, request: AgentRequest) -> AgentResponse:
        """Provider-agnostic placeholder reasoning layer.

        Day 3+ can connect an actual LLM without changing the public Agent
        contract or runtime adapter interface.
        """
        return AgentResponse(
            content=f"Nova received: {request.message}",
            metadata={
                "agent_id": self.agent_id,
                "version": self.version,
                "capabilities": self.capabilities,
            },
        )
