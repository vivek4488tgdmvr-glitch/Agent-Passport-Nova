from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any


class RegistryStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"


@dataclass
class RegistryEntry:
    passport_id: str
    agent_id: str
    name: str
    version: str
    fingerprint: str
    status: RegistryStatus = RegistryStatus.ACTIVE
    issuer: str | None = None
    public_key: str | None = None
    registered_at: str | None = None
    passport: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RegistryEntry":
        data = dict(data)
        data["status"] = RegistryStatus(data.get("status", "active"))
        return cls(**data)
