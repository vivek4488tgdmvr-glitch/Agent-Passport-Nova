from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent_passport.model.base import ModelMessage, ModelProvider, ModelResponse


@dataclass
class LLMBackedAgent:
    """Portable agent shell around a provider-independent model interface."""

    agent_id: str
    name: str
    version: str
    model: ModelProvider
    system_prompt: str = "You are a helpful portable agent."
    capabilities: list[str] = field(default_factory=list)

    def run(self, user_input: str, **kwargs: Any) -> ModelResponse:
        messages = [
            ModelMessage(role="system", content=self.system_prompt),
            ModelMessage(role="user", content=user_input),
        ]
        return self.model.generate(messages, **kwargs)

    def describe(self) -> dict[str, Any]:
        return {
            "id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "model_provider": self.model.provider_name,
            "model": self.model.model_name,
            "capabilities": self.capabilities,
        }
