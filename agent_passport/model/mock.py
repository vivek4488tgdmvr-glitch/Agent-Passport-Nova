from __future__ import annotations

from typing import Any

from .base import ModelMessage, ModelResponse


class MockModelProvider:
    """Deterministic model used for tests and demos without API credentials."""

    provider_name = "mock"
    model_name = "nova-demo-1"

    def generate(
        self,
        messages: list[ModelMessage],
        **kwargs: Any,
    ) -> ModelResponse:
        user_messages = [m.content for m in messages if m.role == "user"]
        prompt = user_messages[-1] if user_messages else ""

        return ModelResponse(
            content=f"Model response: {prompt}",
            model=self.model_name,
            provider=self.provider_name,
            metadata={"deterministic": True},
        )
