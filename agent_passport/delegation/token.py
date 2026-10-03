from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class DelegationToken:
    """A scoped, replay-resistant delegation capability."""

    requester_id: str
    target_id: str
    capabilities: frozenset[str]
    tools: frozenset[str]
    purpose: str
    max_uses: int = 1
    expires_at: str | None = None
    token_id: str = field(default_factory=lambda: uuid4().hex)

    def allows_capability(self, capability: str) -> bool:
        return capability in self.capabilities

    def allows_tool(self, tool_id: str) -> bool:
        return tool_id in self.tools

    def is_expired(self, now: datetime | None = None) -> bool:
        if self.expires_at is None:
            return False
        current = now or datetime.now(timezone.utc)
        expiry = datetime.fromisoformat(self.expires_at.replace("Z", "+00:00"))
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return current >= expiry

    def to_dict(self) -> dict[str, Any]:
        return {
            "requester_id": self.requester_id,
            "target_id": self.target_id,
            "capabilities": sorted(self.capabilities),
            "tools": sorted(self.tools),
            "purpose": self.purpose,
            "max_uses": self.max_uses,
            "expires_at": self.expires_at,
            "token_id": self.token_id,
        }
