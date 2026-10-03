from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class VisaStatus(str, Enum):
    ISSUED = "ISSUED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class FrameworkVisa:
    framework: str
    visa_id: str
    passport_agent_id: str
    passport_version: str
    contract_version: str = "1.0"
    status: VisaStatus = VisaStatus.ISSUED

    def to_dict(self) -> dict[str, Any]:
        return {
            "framework": self.framework,
            "visa_id": self.visa_id,
            "passport_agent_id": self.passport_agent_id,
            "passport_version": self.passport_version,
            "contract_version": self.contract_version,
            "status": self.status.value,
        }


@dataclass(frozen=True)
class FrameworkExport:
    framework: str
    agent_id: str
    passport_version: str
    artifact: dict[str, Any]
    visa: FrameworkVisa

    def to_dict(self) -> dict[str, Any]:
        return {
            "framework": self.framework,
            "agent_id": self.agent_id,
            "passport_version": self.passport_version,
            "artifact": self.artifact,
            "visa": self.visa.to_dict(),
        }
