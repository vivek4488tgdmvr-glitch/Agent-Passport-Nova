from __future__ import annotations

import hashlib
import json
import re
from abc import ABC, abstractmethod
from typing import Any

from agent_passport.core import Agent
from .models import FrameworkExport, FrameworkVisa, VisaStatus


_AGENT_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


class FrameworkVisaAdapter(ABC):
    """Framework export boundary used by the OpenGAP compatibility layer.

    These adapters produce deterministic framework-shaped export artifacts. They
    do not claim that a third-party SDK is installed or that the artifact is an
    official implementation of that framework.
    """

    framework = ""
    adapter_version = "1.0"

    def export(self, agent: Agent) -> FrameworkExport:
        self._validate_agent(agent)
        artifact = self.build_artifact(agent)
        visa_id = self._visa_id(agent, artifact)
        visa = FrameworkVisa(
            framework=self.framework,
            visa_id=visa_id,
            passport_agent_id=agent.agent_id,
            passport_version=agent.version,
            contract_version=self.adapter_version,
            status=VisaStatus.ISSUED,
        )
        return FrameworkExport(
            framework=self.framework,
            agent_id=agent.agent_id,
            passport_version=agent.version,
            artifact=artifact,
            visa=visa,
        )

    @abstractmethod
    def build_artifact(self, agent: Agent) -> dict[str, Any]:
        raise NotImplementedError

    def _validate_agent(self, agent: Agent) -> None:
        if not isinstance(agent, Agent):
            raise TypeError("Visa export requires an Agent instance.")
        if not _AGENT_ID.fullmatch(agent.agent_id):
            raise ValueError("Agent id contains unsupported characters.")
        if not agent.version.strip():
            raise ValueError("Agent version cannot be empty.")

    def _base_artifact(self, agent: Agent) -> dict[str, Any]:
        return {
            "schema": "opengap-framework-export/1.0",
            "agent": {
                "id": agent.agent_id,
                "name": agent.name,
                "version": agent.version,
            },
            "capabilities": sorted(set(agent.capabilities)),
            "tools": sorted(agent.tools.keys()),
            "source": "agent-passport",
            "adapter_version": self.adapter_version,
        }

    def _visa_id(self, agent: Agent, artifact: dict[str, Any]) -> str:
        canonical = json.dumps(artifact, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(canonical).hexdigest()[:20]
        return f"visa-{self.framework}-{agent.agent_id}-{digest}"


class OpenAISDKVisaAdapter(FrameworkVisaAdapter):
    framework = "openai-sdk"

    def build_artifact(self, agent: Agent) -> dict[str, Any]:
        artifact = self._base_artifact(agent)
        artifact["target"] = "OpenAI SDK"
        artifact["entrypoint"] = "responses"
        artifact["instruction"] = f"Run passport agent {agent.agent_id} through an OpenAI-compatible host."
        return artifact


class CrewAIVisaAdapter(FrameworkVisaAdapter):
    framework = "crewai"

    def build_artifact(self, agent: Agent) -> dict[str, Any]:
        artifact = self._base_artifact(agent)
        artifact["target"] = "CrewAI"
        artifact["entrypoint"] = "agent"
        artifact["role"] = agent.name
        artifact["goal"] = "Preserve the Agent Passport identity and behavior contract."
        return artifact


class ClaudeCodeVisaAdapter(FrameworkVisaAdapter):
    framework = "claude-code"

    def build_artifact(self, agent: Agent) -> dict[str, Any]:
        artifact = self._base_artifact(agent)
        artifact["target"] = "Claude Code"
        artifact["entrypoint"] = "agent"
        artifact["instructions"] = f"Operate {agent.name} under the Agent Passport contract."
        return artifact


class LyzrVisaAdapter(FrameworkVisaAdapter):
    framework = "lyzr"

    def build_artifact(self, agent: Agent) -> dict[str, Any]:
        artifact = self._base_artifact(agent)
        artifact["target"] = "Lyzr"
        artifact["entrypoint"] = "agent"
        artifact["agent_type"] = "passport-compatible"
        return artifact
