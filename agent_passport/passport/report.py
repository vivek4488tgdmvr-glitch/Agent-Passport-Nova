from __future__ import annotations

from dataclasses import dataclass, asdict

from .loader import load
from .fingerprint import fingerprint


@dataclass
class Check:
    name: str
    status: str
    detail: str


def verify(path: str) -> dict:
    checks: list[Check] = []

    try:
        passport = load(path)
        checks.append(Check("schema", "PASS", "Passport schema is valid."))
    except Exception as exc:
        return {
            "status": "FAIL",
            "passport": path,
            "checks": [asdict(Check("schema", "FAIL", str(exc)))],
        }

    if passport.agent.id.strip():
        checks.append(Check("identity", "PASS", "Agent identity is present."))
    else:
        checks.append(Check("identity", "FAIL", "Agent ID is empty."))

    if passport.behavior.input.type and passport.behavior.output.type:
        checks.append(Check("behavior", "PASS", "Input/output contracts are defined."))
    else:
        checks.append(Check("behavior", "FAIL", "Behavior contract is incomplete."))

    tool_names = [tool.name for tool in passport.tools]
    unique = len(tool_names) == len(set(tool_names))
    checks.append(
        Check(
            "tools",
            "PASS" if unique else "FAIL",
            "Tool contracts have unique names." if unique else "Duplicate tool names found.",
        )
    )

    runtimes = passport.runtime.compatible
    checks.append(
        Check(
            "runtime",
            "PASS" if runtimes else "FAIL",
            f"{len(runtimes)} compatible runtime(s) declared.",
        )
    )

    overall = "PASS" if all(c.status == "PASS" for c in checks) else "FAIL"
    return {
        "status": overall,
        "passport": path,
        "agent": passport.agent.name,
        "agent_version": passport.agent.version,
        "fingerprint": fingerprint(passport),
        "checks": [asdict(c) for c in checks],
    }
