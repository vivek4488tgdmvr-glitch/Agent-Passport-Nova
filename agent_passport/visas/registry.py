from __future__ import annotations

from typing import Any

from agent_passport.core import Agent
from .adapters import (
    ClaudeCodeVisaAdapter,
    CrewAIVisaAdapter,
    FrameworkVisaAdapter,
    LyzrVisaAdapter,
    OpenAISDKVisaAdapter,
)
from .models import FrameworkExport

_ADAPTERS: dict[str, type[FrameworkVisaAdapter]] = {
    "openai-sdk": OpenAISDKVisaAdapter,
    "crewai": CrewAIVisaAdapter,
    "claude-code": ClaudeCodeVisaAdapter,
    "lyzr": LyzrVisaAdapter,
}


def export_framework(agent: Agent, framework: str) -> FrameworkExport:
    key = framework.strip().lower()
    if key not in _ADAPTERS:
        raise KeyError(f"Unsupported framework visa target: {framework}")
    return _ADAPTERS[key]().export(agent)


def export_all_visas(agent: Agent) -> dict[str, FrameworkExport]:
    return {name: adapter().export(agent) for name, adapter in _ADAPTERS.items()}


def verify_export(export: FrameworkExport) -> bool:
    visa = export.visa
    return (
        visa.status.value == "ISSUED"
        and visa.framework == export.framework
        and visa.passport_agent_id == export.agent_id
        and visa.passport_version == export.passport_version
        and export.artifact.get("agent", {}).get("id") == export.agent_id
        and export.artifact.get("agent", {}).get("version") == export.passport_version
    )
