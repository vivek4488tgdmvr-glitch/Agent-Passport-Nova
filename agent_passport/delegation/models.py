from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentPeer:
    """Minimal trust record for an agent participating in delegation."""

    agent_id: str
    name: str
    version: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    tools: frozenset[str] = field(default_factory=frozenset)
    issuer: str | None = None
    passport_fingerprint: str | None = None

    def has_capabilities(self, required: set[str] | frozenset[str]) -> bool:
        return set(required).issubset(self.capabilities)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "capabilities": sorted(self.capabilities),
            "tools": sorted(self.tools),
            "issuer": self.issuer,
            "passport_fingerprint": self.passport_fingerprint,
        }


@dataclass(frozen=True)
class DelegationRequest:
    requester_id: str
    target_id: str
    capabilities: frozenset[str] = field(default_factory=frozenset)
    tools: frozenset[str] = field(default_factory=frozenset)
    purpose: str = ""
    max_uses: int = 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "requester_id": self.requester_id,
            "target_id": self.target_id,
            "capabilities": sorted(self.capabilities),
            "tools": sorted(self.tools),
            "purpose": self.purpose,
            "max_uses": self.max_uses,
        }


@dataclass(frozen=True)
class DelegationResult:
    status: str
    requester_id: str
    target_id: str
    missing_capabilities: tuple[str, ...] = ()
    missing_tools: tuple[str, ...] = ()
    reason: str = ""

    @property
    def allowed(self) -> bool:
        return self.status == "ALLOWED"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "requester_id": self.requester_id,
            "target_id": self.target_id,
            "missing_capabilities": list(self.missing_capabilities),
            "missing_tools": list(self.missing_tools),
            "reason": self.reason,
        }

    def pretty(self) -> str:
        lines = [
            "DELEGATION CHECK",
            "----------------",
            f"Status: {self.status}",
            f"Requester: {self.requester_id}",
            f"Target: {self.target_id}",
        ]
        if self.missing_capabilities:
            lines.append(
                "Missing capabilities: " +
                ", ".join(self.missing_capabilities)
            )
        if self.missing_tools:
            lines.append("Missing tools: " + ", ".join(self.missing_tools))
        if self.reason:
            lines.append(f"Reason: {self.reason}")
        return "\n".join(lines)
