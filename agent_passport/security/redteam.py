"""Safe, deterministic red-team probes for Agent Passport defenses.

These probes exercise the application's security boundaries without scanning,
exploiting, or attacking external systems. They are intended for CI and demos.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

from .hardening import RequestGuard, ReplayGuard, SlidingWindowRateLimiter, TamperEvidentAuditLog, redact_secrets
from .policy import PermissionPolicy
from .sandbox import SandboxLimits, ToolSandbox


@dataclass(frozen=True)
class ProbeResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class RedTeamReport:
    probes: tuple[ProbeResult, ...]

    @property
    def passed(self) -> int:
        return sum(p.passed for p in self.probes)

    @property
    def total(self) -> int:
        return len(self.probes)

    @property
    def status(self) -> str:
        return "PASS" if self.passed == self.total else "FAIL"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "passed": self.passed,
            "total": self.total,
            "probes": [p.__dict__ for p in self.probes],
        }

    def pretty(self) -> str:
        lines = ["AGENT PASSPORT — SAFE RED-TEAM REPORT", "=" * 42]
        for p in self.probes:
            lines.append(f"{'✓' if p.passed else '✗'} {p.name}: {p.detail}")
        lines.append(f"RESULT: {self.passed}/{self.total} probes passed — {self.status}")
        return "\n".join(lines)


def _probe(name: str, fn: Callable[[], bool], detail: str) -> ProbeResult:
    try:
        return ProbeResult(name, bool(fn()), detail)
    except Exception as exc:
        return ProbeResult(name, False, f"unexpected error: {type(exc).__name__}: {exc}")


def run_red_team_suite() -> RedTeamReport:
    """Run local attack simulations against the security controls."""
    probes: list[ProbeResult] = []

    guard = RequestGuard(max_body_bytes=16)
    probes.append(_probe("Malformed principal", lambda: not guard.validate("../../etc/passwd").allowed, "path-like identity rejected"))
    probes.append(_probe("Oversized request", lambda: not guard.validate("nova", body=b"x" * 17).allowed, "request-size limit enforced"))

    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60, clock=lambda: 1.0)
    limiter.allow("attacker")
    limiter.allow("attacker")
    probes.append(_probe("Rate-limit flood", lambda: not limiter.allow("attacker"), "third request blocked"))

    replay = ReplayGuard(max_entries=100)
    replay.accept_once("nonce-1")
    probes.append(_probe("Replay request", lambda: not replay.accept_once("nonce-1"), "duplicate nonce rejected"))

    probes.append(_probe("Privilege escalation", lambda: not PermissionPolicy(allow=frozenset({"network"}), deny=frozenset({"shell"})).evaluate({"network", "shell"}).value == "ALLOW", "denied permission overrides allowed permission"))

    secrets = redact_secrets({"api_key": "SECRET", "nested": {"password": "PASS"}, "safe": "ok"})
    probes.append(_probe("Credential leakage", lambda: secrets["api_key"] == "[REDACTED]" and secrets["nested"]["password"] == "[REDACTED]", "credential fields redacted"))

    audit = TamperEvidentAuditLog()
    audit.append("AUTHZ", principal="attacker", result="DENY", details={"token": "SECRET"})
    probes.append(_probe("Audit integrity", lambda: audit.verify() and audit.entries()[0]["details"]["token"] == "[REDACTED]", "hash chain verifies and secrets are absent"))

    audit.append("ACTION", principal="attacker", result="DENY")
    entry = audit._entries[0]
    entry["result"] = "ALLOW"
    probes.append(_probe("Audit tampering", lambda: not audit.verify(), "modified historical event detected"))

    sandbox = ToolSandbox(PermissionPolicy(allow=frozenset()), limits=SandboxLimits(timeout_seconds=0.05))
    probes.append(_probe("Sandbox timeout", lambda: sandbox.execute(lambda: time.sleep(1), set()).status == "TIMEOUT", "runaway handler terminated"))

    probes.append(_probe("Unauthorized tool", lambda: sandbox.execute(lambda: "executed", {"shell"}).status == "DENY", "tool blocked before handler execution"))

    report_audit = TamperEvidentAuditLog()
    report_audit.append("REDTEAM", principal="ci", result="PASS", details={"suite": "safe-local"})
    probes.append(_probe("Evidence chain", lambda: report_audit.verify(), "red-team result can be backed by a valid audit chain"))

    return RedTeamReport(tuple(probes))
