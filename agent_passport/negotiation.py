"""Capability negotiation between a Passport and a target runtime."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NegotiationResult:
    compatible: bool
    required: list[str] = field(default_factory=list)
    provided: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "COMPATIBLE" if self.compatible else "INCOMPATIBLE"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "compatible": self.compatible,
            "required": self.required,
            "provided": self.provided,
            "missing": self.missing,
            "conflicts": self.conflicts,
        }

    def pretty(self) -> str:
        lines = [
            "CAPABILITY NEGOTIATION",
            "-" * 48,
            f"Status: {self.status}",
            f"Required: {', '.join(self.required) or '(none)'}",
            f"Provided: {', '.join(self.provided) or '(none)'}",
        ]
        if self.missing:
            lines.append("Missing:")
            lines.extend(f"  ✗ {item}" for item in self.missing)
        if self.conflicts:
            lines.append("Conflicts:")
            lines.extend(f"  ! {item}" for item in self.conflicts)
        if self.compatible:
            lines.append("✓ Target runtime satisfies Passport requirements.")
        return "\n".join(lines)


def _passport_requirements(passport: dict[str, Any]) -> list[str]:
    identity = passport.get("identity", {})
    capabilities = identity.get("capabilities", [])
    return sorted(set(str(x) for x in capabilities))


def _runtime_capabilities(runtime: Any) -> list[str]:
    if isinstance(runtime, dict):
        values = runtime.get("capabilities", [])
    else:
        values = getattr(runtime, "capabilities", [])
    return sorted(set(str(x) for x in values))


def negotiate(
    passport: dict[str, Any],
    runtime: Any,
    *,
    conflicts: list[str] | None = None,
) -> NegotiationResult:
    required = _passport_requirements(passport)
    provided = _runtime_capabilities(runtime)
    missing = sorted(set(required) - set(provided))
    conflict_list = sorted(set(conflicts or []))
    return NegotiationResult(
        compatible=not missing and not conflict_list,
        required=required,
        provided=provided,
        missing=missing,
        conflicts=conflict_list,
    )


def require_compatible(
    passport: dict[str, Any],
    runtime: Any,
    *,
    conflicts: list[str] | None = None,
) -> NegotiationResult:
    result = negotiate(passport, runtime, conflicts=conflicts)
    if not result.compatible:
        raise RuntimeError(result.pretty())
    return result
