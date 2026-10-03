from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BehaviorCase:
    """A deterministic behavioral expectation for an agent."""

    name: str
    input: Any
    expected_output: Any = None
    expected_output_type: str | None = None
    expected_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "input": self.input,
            "expected_output": self.expected_output,
            "expected_output_type": self.expected_output_type,
            "expected_error": self.expected_error,
        }


@dataclass(frozen=True)
class CaseResult:
    name: str
    status: str
    actual_output: Any = None
    error: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "actual_output": self.actual_output,
            "error": self.error,
            "reason": self.reason,
        }


@dataclass
class ConformanceReport:
    results: list[CaseResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(r.status == "PASS" for r in self.results)

    @property
    def failed(self) -> int:
        return sum(r.status == "FAIL" for r in self.results)

    @property
    def status(self) -> str:
        return "PASS" if self.results and self.failed == 0 else (
            "PASS" if not self.results else "FAIL"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "total": len(self.results),
            "passed": self.passed,
            "failed": self.failed,
            "cases": [r.to_dict() for r in self.results],
        }

    def pretty(self) -> str:
        lines = [
            "BEHAVIORAL CONFORMANCE REPORT",
            "------------------------------",
            f"Status: {self.status}",
            f"Cases: {len(self.results)}",
            f"Passed: {self.passed}",
            f"Failed: {self.failed}",
        ]
        for result in self.results:
            mark = "✓" if result.status == "PASS" else "✗"
            lines.append(f"{mark} {result.name}: {result.status}")
            if result.reason:
                lines.append(f"    {result.reason}")
        return "\n".join(lines)
