from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ModelMessage:
    role: str
    content: str


@dataclass
class ModelResponse:
    content: str
    model: str
    provider: str
    raw: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelProvider(Protocol):
    """Provider-independent model contract."""

    provider_name: str
    model_name: str

    def generate(
        self,
        messages: list[ModelMessage],
        **kwargs: Any,
    ) -> ModelResponse:
        ...
