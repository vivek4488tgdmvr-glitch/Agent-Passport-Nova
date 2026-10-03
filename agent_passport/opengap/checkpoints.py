from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable

from .schema import OpenGAPValidationError, validate_agent_yaml


@dataclass(frozen=True)
class CheckpointResult:
    id: str
    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


@dataclass(frozen=True)
class CheckpointReport:
    status: str
    checkpoints: tuple[CheckpointResult, ...]
    repository: str

    @property
    def passed_count(self) -> int:
        return sum(item.passed for item in self.checkpoints)

    @property
    def total(self) -> int:
        return len(self.checkpoints)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "repository": self.repository,
            "passed": self.passed_count,
            "total": self.total,
            "checkpoints": [asdict(item) for item in self.checkpoints],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=False)

    def pretty(self) -> str:
        lines = [
            "OPENGAP PASSPORT CHECKPOINTS",
            "=" * 32,
            f"Status: {self.status}",
            f"Passed: {self.passed_count}/{self.total}",
        ]
        for item in self.checkpoints:
            lines.append(f"{item.id}. {item.name}: {item.status} — {item.detail}")
        return "\n".join(lines)


def _validate(root: Path) -> str:
    doc = validate_agent_yaml(root / "agent.yaml")
    return f"spec {doc.spec}; agent {doc.agent['id']} v{doc.agent['version']}"


def _explain(root: Path) -> str:
    path = root / "EXPLAINABILITY.md"
    if not path.is_file():
        raise FileNotFoundError("missing root EXPLAINABILITY.md")
    text = path.read_text(encoding="utf-8").strip()
    if len(text) < 200:
        raise ValueError("EXPLAINABILITY.md is too short to document decisions, data, and limitations")
    lowered = text.lower()
    required_topics = ("decision", "data", "limitation")
    missing = [topic for topic in required_topics if topic not in lowered]
    if missing:
        raise ValueError("EXPLAINABILITY.md is missing topics: " + ", ".join(missing))
    return f"{len(text)} characters; decisions, data, and limitations documented"


def _passport(root: Path) -> str:
    passport = root / "passport.yaml"
    evidence = root / "passport-travel-evidence-signed.json"
    audit = root / "security-audit-report.json"
    missing = [str(p.name) for p in (passport, evidence, audit) if not p.is_file()]
    if missing:
        raise FileNotFoundError("missing evidence artifacts: " + ", ".join(missing))
    from agent_passport.passport.evidence import verify_evidence
    from agent_passport.passport.fingerprint import fingerprint
    from agent_passport.passport.loader import load

    json.loads(audit.read_text(encoding="utf-8"))
    signed = json.loads(evidence.read_text(encoding="utf-8"))
    result = verify_evidence(signed, fingerprint(load(passport)))
    if result.get("status") != "PASS":
        raise ValueError("signed evidence failed verification: " + str(result.get("reason", result.get("status"))))
    return "Passport present; signed travel evidence cryptographically verified and bound to passport.yaml"


_CHECKS: tuple[tuple[str, str, Callable[[Path], str]], ...] = (
    ("01", "VALIDATE", _validate),
    ("02", "EXPLAIN", _explain),
    ("03", "PASSPORT EVIDENCE", _passport),
)


def run_checkpoints(root: str | Path = ".") -> CheckpointReport:
    root_path = Path(root).resolve()
    results: list[CheckpointResult] = []
    for checkpoint_id, name, check in _CHECKS:
        try:
            detail = check(root_path)
            results.append(CheckpointResult(checkpoint_id, name, "PASS", detail))
        except (OSError, ValueError, OpenGAPValidationError, json.JSONDecodeError) as exc:
            results.append(CheckpointResult(checkpoint_id, name, "FAIL", str(exc)))
    status = "PASS" if all(item.passed for item in results) else "FAIL"
    return CheckpointReport(status=status, checkpoints=tuple(results), repository=str(root_path))
