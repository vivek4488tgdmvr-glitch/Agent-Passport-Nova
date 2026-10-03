from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class OpenGAPValidationError(ValueError):
    """Raised when an OpenGAP compatibility document is malformed."""


class Behavior(BaseModel):
    model_config = ConfigDict(extra="forbid")
    input: dict[str, Any]
    output: dict[str, Any]


class Tool(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_type: str = "json"


class FrameworkExports(BaseModel):
    model_config = ConfigDict(extra="forbid")
    targets: list[str] = Field(default_factory=list)


class SecurityProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")
    signed_identity: bool = False
    least_privilege: bool = False
    sandboxed_tools: bool = False
    replay_protection: bool = False
    audit_logging: bool = False


class OpenGAPAgent(BaseModel):
    """Local compatibility profile for the challenge-facing root agent.yaml.

    This is intentionally a strict, versioned boundary. It does not claim to
    be the challenge validator's private implementation; it makes the
    repository self-validating against the public shape shown in the brief.
    """

    model_config = ConfigDict(extra="forbid")
    spec: str
    agent: dict[str, Any]
    capabilities: list[str] = Field(default_factory=list)
    behavior: Behavior
    tools: list[Tool] = Field(default_factory=list)
    frameworks: FrameworkExports = Field(default_factory=FrameworkExports)
    security: SecurityProfile = Field(default_factory=SecurityProfile)

    @field_validator("spec")
    @classmethod
    def validate_spec(cls, value: str) -> str:
        if value != "0.1.0":
            raise ValueError("OpenGAP compatibility profile requires spec 0.1.0")
        return value

    @field_validator("agent")
    @classmethod
    def validate_agent(cls, value: dict[str, Any]) -> dict[str, Any]:
        required = {"id", "name", "version", "description"}
        missing = sorted(required - value.keys())
        if missing:
            raise ValueError(f"agent is missing required fields: {', '.join(missing)}")
        for key in required:
            if not isinstance(value[key], str) or not value[key].strip():
                raise ValueError(f"agent.{key} must be a non-empty string")
        return value


def load_agent_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if path.name != "agent.yaml":
        raise OpenGAPValidationError("OpenGAP entrypoint must be a root-level agent.yaml")
    if not path.exists():
        raise FileNotFoundError(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise OpenGAPValidationError(f"invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise OpenGAPValidationError("agent.yaml root must be a mapping")
    return raw


def validate_agent_yaml(path: str | Path) -> OpenGAPAgent:
    raw = load_agent_yaml(path)
    try:
        return OpenGAPAgent.model_validate(raw)
    except ValidationError as exc:
        raise OpenGAPValidationError(str(exc)) from exc
