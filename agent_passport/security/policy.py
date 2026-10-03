"""Declarative security policies for agents and tools."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class PermissionDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


@dataclass(frozen=True)
class PermissionPolicy:
    """Explicit allow/deny policy.

    A permission is allowed only when explicitly allowed and not explicitly
    denied. Deny takes precedence if both sets contain the permission.
    """
    allow: frozenset[str] = field(default_factory=frozenset)
    deny: frozenset[str] = field(default_factory=frozenset)

    def evaluate(self, requested: set[str] | frozenset[str]) -> PermissionDecision:
        requested = set(requested)
        if requested & set(self.deny):
            return PermissionDecision.DENY
        if not requested.issubset(set(self.allow)):
            return PermissionDecision.DENY
        return PermissionDecision.ALLOW

    def to_dict(self) -> dict[str, list[str]]:
        return {
            "allow": sorted(self.allow),
            "deny": sorted(self.deny),
        }
