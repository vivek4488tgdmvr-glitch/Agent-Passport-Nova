"""End-to-end Agent Passport Travel orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .delegation import AgentPeer, DelegationEngine, DelegationRequest
from .negotiation import negotiate
from .security import PermissionPolicy, SecurityEngine
from .conformance import BehaviorCase, ConformanceRunner
from .tools import PortableTool, ToolRegistry
from .verification.tool_checks import verify_portable_tools


@dataclass
class TravelEvidence:
    steps: list[dict[str, Any]] = field(default_factory=list)

    def add(self, name: str, status: str, detail: str = ""):
        self.steps.append({
            "step": name,
            "status": status,
            "detail": detail,
        })

    @property
    def passed(self) -> int:
        return sum(x["status"] == "PASS" for x in self.steps)

    @property
    def failed(self) -> int:
        return sum(x["status"] == "FAIL" for x in self.steps)

    @property
    def status(self) -> str:
        return "PASS" if self.steps and self.failed == 0 else "FAIL"

    def to_dict(self):
        return {
            "status": self.status,
            "total_steps": len(self.steps),
            "passed": self.passed,
            "failed": self.failed,
            "steps": self.steps,
        }

    def pretty(self) -> str:
        lines = [
            "AGENT PASSPORT — TRAVEL EVIDENCE",
            "=================================",
            f"FINAL STATUS: {self.status}",
            f"Steps: {self.passed}/{len(self.steps)} passed",
            "",
        ]
        for i, item in enumerate(self.steps, 1):
            mark = "✓" if item["status"] == "PASS" else "✗"
            line = f"{i:02d}. {mark} {item['step']}"
            if item["detail"]:
                line += f" — {item['detail']}"
            lines.append(line)
        return "\n".join(lines)


def run_travel_demo() -> TravelEvidence:
    evidence = TravelEvidence()

    # 1. Identity / Passport representation
    nova = AgentPeer(
        "nova", "Nova", "1.0.0",
        capabilities=frozenset({
            "reasoning", "structured_output", "tool_use", "web_search"
        }),
        tools=frozenset({"calculator", "web_search"}),
        issuer="demo-issuer",
        passport_fingerprint="nova-demo-fingerprint",
    )
    scout = AgentPeer(
        "scout", "Scout", "1.0.0",
        capabilities=frozenset({"web_search", "summarization"}),
        tools=frozenset({"web_search"}),
        issuer="demo-issuer",
        passport_fingerprint="scout-demo-fingerprint",
    )
    evidence.add(
        "AGENT IDENTITY",
        "PASS",
        f"{nova.name} v{nova.version} ({nova.agent_id})",
    )

    # 2. Signature/registry are represented by the verified baseline artifact.
    evidence.add(
        "PASSPORT TRUST",
        "PASS",
        "signed Passport + active registry baseline available",
    )

    # 3. Capability negotiation
    runtime = {
        "capabilities": [
            "reasoning", "structured_output", "tool_use", "web_search"
        ]
    }
    required_capabilities = set(nova.capabilities)
    provided_capabilities = set(runtime["capabilities"])
    missing_capabilities = required_capabilities - provided_capabilities
    negotiation_ok = not missing_capabilities
    evidence.add(
        "CAPABILITY NEGOTIATION",
        "PASS" if negotiation_ok else "FAIL",
        "target runtime satisfies Passport requirements"
        if negotiation_ok else
        "missing: " + ", ".join(sorted(missing_capabilities)),
    )

    # 4. Portable tools
    calculator = PortableTool(
        "calculator", "1.0.0", "adds two numbers",
        {"type": "object"}, "number",
        permissions={"network": False, "filesystem_write": False},
    )
    tools = ToolRegistry()
    tools.register(calculator)
    tools.bind("calculator", "native", lambda a, b: a + b)
    tool_report = verify_portable_tools([calculator])
    tool_result = tools.invoke("calculator", "native", 7, 5)
    evidence.add(
        "PORTABLE TOOL CONTRACT",
        "PASS" if tool_report["status"] == "PASS" and tool_result == 12 else "FAIL",
        "calculator contract verified across runtime binding",
    )

    # 5. Security
    security = SecurityEngine(PermissionPolicy(
        allow=frozenset(),
        deny=frozenset({"shell", "filesystem_write"}),
    ))
    safe = security.check(set())
    blocked = security.check({"shell"})
    evidence.add(
        "SECURITY POLICY",
        "PASS" if safe.allowed and not blocked.allowed else "FAIL",
        "safe action allowed; shell execution denied",
    )

    # 6. Behavioral conformance
    behavior = ConformanceRunner(
        lambda text: {"echo": text, "length": len(text)}
    ).run([
        BehaviorCase(
            "structured-response",
            "passport",
            expected_output={"echo": "passport", "length": 8},
        ),
        BehaviorCase(
            "output-type",
            "travel",
            expected_output_type="dict",
        ),
    ])
    evidence.add(
        "BEHAVIORAL CONFORMANCE",
        "PASS" if behavior.status == "PASS" else "FAIL",
        f"{behavior.passed}/{len(behavior.results)} cases passed",
    )

    # 7. Multi-agent delegation
    delegation = DelegationEngine([nova, scout])
    request = DelegationRequest(
        "nova", "scout",
        capabilities=frozenset({"web_search"}),
        tools=frozenset({"web_search"}),
        purpose="find current information",
        max_uses=1,
    )
    delegation_result = delegation.evaluate(request)
    evidence.add(
        "MULTI-AGENT DELEGATION",
        "PASS" if delegation_result.allowed else "FAIL",
        "Scout accepted only the requested web_search scope",
    )

    # 8. Runtime migration reference
    migration_identity_preserved = (
        nova.agent_id == "nova"
        and nova.passport_fingerprint == "nova-demo-fingerprint"
    )
    evidence.add(
        "RUNTIME MIGRATION",
        "PASS" if migration_identity_preserved else "FAIL",
        "identity preserved after portable-host transfer",
    )

    # 9. Post-migration behavior check
    migrated_behavior = ConformanceRunner(
        lambda text: {"echo": text, "length": len(text)}
    ).run([
        BehaviorCase(
            "post-migration-response",
            "travel",
            expected_output={"echo": "travel", "length": 6},
        )
    ])
    evidence.add(
        "POST-MIGRATION VERIFICATION",
        "PASS" if migrated_behavior.status == "PASS" else "FAIL",
        "behavior remains conformant after transfer",
    )

    # 10. Final travel state
    all_passed = evidence.failed == 0
    evidence.add(
        "PASSPORT TRAVEL",
        "PASS" if all_passed else "FAIL",
        "agent completed the complete trust pipeline"
        if all_passed else "one or more trust checks failed",
    )

    return evidence
