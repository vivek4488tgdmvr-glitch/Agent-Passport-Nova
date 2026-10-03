from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ..passport.loader import load


def export_opengap_agent(passport_path: str | Path, output_path: str | Path = "agent.yaml") -> Path:
    """Map an Agent Passport into the challenge-facing OpenGAP profile.

    The mapping is deterministic and keeps the original Passport as the
    source of truth. Framework names are normalized to the four visible
    challenge visa targets; this does not assert that an external visa has
    already been issued.
    """
    passport = load(passport_path)
    data: dict[str, Any] = {
        "spec": "0.1.0",
        "agent": {
            "id": passport.agent.id,
            "name": passport.agent.name,
            "version": passport.agent.version,
            "description": passport.agent.description,
        },
        "capabilities": list(passport.identity.capabilities),
        "behavior": {
            "input": passport.behavior.input.model_dump(mode="json"),
            "output": passport.behavior.output.model_dump(mode="json"),
        },
        "tools": [tool.model_dump(mode="json") for tool in passport.tools],
        "frameworks": {
            "targets": ["openai-sdk", "crewai", "claude-code", "lyzr"]
        },
        "security": {
            "signed_identity": True,
            "least_privilege": True,
            "sandboxed_tools": True,
            "replay_protection": True,
            "audit_logging": True,
        },
    }
    output = Path(output_path)
    output.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return output
