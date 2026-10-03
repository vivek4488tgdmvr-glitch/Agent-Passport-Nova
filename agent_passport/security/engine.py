from __future__ import annotations

from dataclasses import dataclass
from .policy import PermissionDecision, PermissionPolicy


@dataclass(frozen=True)
class SecurityResult:
    decision: PermissionDecision
    requested: tuple[str, ...]
    missing: tuple[str, ...] = ()
    denied: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.decision == PermissionDecision.ALLOW

    def to_dict(self) -> dict:
        return {
            "decision": self.decision.value,
            "requested": list(self.requested),
            "missing": list(self.missing),
            "denied": list(self.denied),
        }

    def pretty(self) -> str:
        lines = [
            "SECURITY POLICY CHECK",
            "---------------------",
            f"Decision: {self.decision.value}",
            f"Requested: {', '.join(self.requested) or '(none)'}",
        ]
        if self.missing:
            lines.append(f"Missing allow: {', '.join(self.missing)}")
        if self.denied:
            lines.append(f"Explicitly denied: {', '.join(self.denied)}")
        return "\n".join(lines)


class SecurityEngine:
    """Evaluates runtime policy before a tool/action is executed."""

    def __init__(self, policy: PermissionPolicy):
        self.policy = policy

    def check(self, requested: set[str] | frozenset[str]) -> SecurityResult:
        requested = set(requested)
        missing = requested - set(self.policy.allow)
        denied = requested & set(self.policy.deny)

        decision = self.policy.evaluate(requested)
        return SecurityResult(
            decision=decision,
            requested=tuple(sorted(requested)),
            missing=tuple(sorted(missing)),
            denied=tuple(sorted(denied)),
        )

    def require(self, requested: set[str] | frozenset[str]) -> SecurityResult:
        result = self.check(requested)
        if not result.allowed:
            raise PermissionError(result.pretty())
        return result
