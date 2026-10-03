from __future__ import annotations

import json
import os
from typing import Any
from urllib.request import Request, urlopen

from .base import ModelMessage, ModelResponse


class OpenAICompatibleProvider:
    """Minimal dependency-free adapter for OpenAI-compatible chat APIs.

    The provider is intentionally generic: endpoint, API key, and model are
    supplied through arguments or environment variables. No provider SDK is
    required, keeping the Agent Passport core provider-independent.
    """

    provider_name = "openai-compatible"

    def __init__(
        self,
        model_name: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 60,
    ):
        self.model_name = model_name or os.getenv("AGENT_MODEL", "example-model")
        self.base_url = (
            base_url
            or os.getenv("AGENT_API_BASE_URL")
            or "https://api.openai.com/v1"
        ).rstrip("/")
        self.api_key = api_key or os.getenv("AGENT_API_KEY")
        self.timeout = timeout

    def generate(
        self,
        messages: list[ModelMessage],
        **kwargs: Any,
    ) -> ModelResponse:
        if not self.api_key:
            raise RuntimeError(
                "AGENT_API_KEY is not configured. "
                "Set it only when you want to call a real provider."
            )

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            **kwargs,
        }

        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urlopen(request, timeout=self.timeout) as response:
            raw = json.loads(response.read().decode("utf-8"))

        content = raw["choices"][0]["message"]["content"]

        return ModelResponse(
            content=content,
            model=self.model_name,
            provider=self.provider_name,
            raw=raw,
            metadata={"endpoint": self.base_url},
        )
