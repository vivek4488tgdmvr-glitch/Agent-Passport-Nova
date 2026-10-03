from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class AgentRequest:
    message: str
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


class Runtime(Protocol):
    """Common interface every runtime adapter must implement."""

    runtime_name: str

    def initialize(self) -> None:
        ...

    def run(self, request: AgentRequest) -> AgentResponse:
        ...

    def shutdown(self) -> None:
        ...
