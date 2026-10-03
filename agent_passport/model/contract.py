from __future__ import annotations

from typing import Any

from .base import ModelMessage, ModelResponse


def validate_model_response(response: ModelResponse) -> dict[str, Any]:
    """Validate the stable fields expected by Agent Passport."""
    checks = {
        "content": isinstance(response.content, str) and bool(response.content),
        "provider": isinstance(response.provider, str) and bool(response.provider),
        "model": isinstance(response.model, str) and bool(response.model),
    }

    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
    }


def build_model_contract(provider: Any) -> dict[str, str]:
    return {
        "interface_version": "1.0",
        "provider": getattr(provider, "provider_name", "unknown"),
        "model": getattr(provider, "model_name", "unknown"),
    }
