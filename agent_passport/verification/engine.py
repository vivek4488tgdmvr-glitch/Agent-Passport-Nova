from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, Any

from agent_passport.core import Agent, AgentRequest
from agent_passport.passport.loader import load


@dataclass
class VerificationCheck:
    name: str
    status: str
    detail: str


class VerificationEngine:
    """Runs deterministic checks against a passport and its agent."""

    def __init__(self, agent: Agent, passport_path: str):
        self.agent = agent
        self.passport_path = passport_path
        self.checks: list[VerificationCheck] = []

    def check_identity(self) -> None:
        passport = load(self.passport_path)
        ok = (
            self.agent.agent_id == passport.agent.id
            and self.agent.name == passport.agent.name
            and self.agent.version == passport.agent.version
        )
        self.checks.append(
            VerificationCheck(
                "identity_match",
                "PASS" if ok else "FAIL",
                "Runtime agent identity matches passport."
                if ok else "Runtime agent identity differs from passport.",
            )
        )

    def check_capabilities(self) -> None:
        passport = load(self.passport_path)
        expected = set(passport.identity.capabilities)
        actual = set(self.agent.capabilities)
        missing = sorted(expected - actual)
        ok = not missing
        self.checks.append(
            VerificationCheck(
                "capabilities",
                "PASS" if ok else "FAIL",
                "All passport capabilities are present."
                if ok else f"Missing capabilities: {missing}",
            )
        )

    def check_tools(self) -> None:
        passport = load(self.passport_path)
        expected = {tool.name for tool in passport.tools}
        actual = set(self.agent.tools)
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        ok = not missing
        detail = "All passport tools are registered."
        if missing:
            detail = f"Missing tools: {missing}"
        elif extra:
            detail = f"All required tools present; extra tools: {extra}"
        self.checks.append(
            VerificationCheck("tools", "PASS" if ok else "FAIL", detail)
        )

    def check_behavior(self) -> None:
        response = self.agent.handle(AgentRequest("verification ping"))
        ok = bool(response.content) and response.metadata.get("agent_id") == self.agent.agent_id
        self.checks.append(
            VerificationCheck(
                "behavior",
                "PASS" if ok else "FAIL",
                "Agent produced a valid response contract."
                if ok else "Agent response contract failed.",
            )
        )

    def check_runtime(self, runtime: Any) -> None:
        passport = load(self.passport_path)
        compatible = set(passport.runtime.compatible)
        name = getattr(runtime, "runtime_name", "unknown")
        ok = name in compatible

        self.checks.append(
            VerificationCheck(
                "runtime_compatibility",
                "PASS" if ok else "FAIL",
                f"Runtime '{name}' is declared compatible."
                if ok else f"Runtime '{name}' is not declared compatible.",
            )
        )

    def run(self, runtime: Any | None = None) -> dict[str, Any]:
        self.checks = []
        try:
            self.check_identity()
            self.check_capabilities()
            self.check_tools()
            self.check_behavior()
            if runtime is not None:
                self.check_runtime(runtime)
        except Exception as exc:
            self.checks.append(VerificationCheck("engine", "FAIL", str(exc)))

        status = "PASS" if all(c.status == "PASS" for c in self.checks) else "FAIL"
        return {
            "status": status,
            "agent": self.agent.name,
            "checks": [asdict(c) for c in self.checks],
        }
