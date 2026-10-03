from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

from agent_passport.passport.fingerprint import fingerprint
from agent_passport.passport.loader import load


@dataclass(frozen=True)
class MigrationManifest:
    agent_id: str
    agent_name: str
    agent_version: str
    passport_fingerprint: str
    source_runtime: str
    target_runtime: str
    model_interface_version: str
    capabilities: tuple[str, ...]
    tools: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_manifest(
    passport_path: str,
    source_runtime: str,
    target_runtime: str,
) -> MigrationManifest:
    passport = load(passport_path)

    return MigrationManifest(
        agent_id=passport.agent.id,
        agent_name=passport.agent.name,
        agent_version=passport.agent.version,
        passport_fingerprint=fingerprint(passport),
        source_runtime=source_runtime,
        target_runtime=target_runtime,
        model_interface_version=passport.model.interface_version,
        capabilities=tuple(passport.identity.capabilities),
        tools=tuple(tool.name for tool in passport.tools),
    )
