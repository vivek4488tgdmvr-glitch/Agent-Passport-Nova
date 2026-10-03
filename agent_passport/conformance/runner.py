from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from .models import BehaviorCase, CaseResult, ConformanceReport


class ConformanceRunner:
    """Runs deterministic behavior cases against an agent-like callable."""

    def __init__(self, handler: Callable[[Any], Any]):
        self.handler = handler

    def run(self, cases: Iterable[BehaviorCase]) -> ConformanceReport:
        report = ConformanceReport()

        for case in cases:
            try:
                actual = self.handler(case.input)
            except Exception as exc:
                if case.expected_error is not None:
                    actual_error = type(exc).__name__
                    if actual_error == case.expected_error:
                        report.results.append(
                            CaseResult(
                                case.name,
                                "PASS",
                                error=actual_error,
                                reason="Expected error observed.",
                            )
                        )
                    else:
                        report.results.append(
                            CaseResult(
                                case.name,
                                "FAIL",
                                error=actual_error,
                                reason=(
                                    f"Expected error {case.expected_error}, "
                                    f"got {actual_error}."
                                ),
                            )
                        )
                else:
                    report.results.append(
                        CaseResult(
                            case.name,
                            "FAIL",
                            error=type(exc).__name__,
                            reason="Unexpected exception.",
                        )
                    )
                continue

            if case.expected_error is not None:
                report.results.append(
                    CaseResult(
                        case.name,
                        "FAIL",
                        actual_output=actual,
                        reason=f"Expected error {case.expected_error}, but call succeeded.",
                    )
                )
                continue

            if case.expected_output_type is not None:
                actual_type = type(actual).__name__
                if actual_type != case.expected_output_type:
                    report.results.append(
                        CaseResult(
                            case.name,
                            "FAIL",
                            actual_output=actual,
                            reason=(
                                f"Expected type {case.expected_output_type}, "
                                f"got {actual_type}."
                            ),
                        )
                    )
                    continue

            if case.expected_output is not None and actual != case.expected_output:
                report.results.append(
                    CaseResult(
                        case.name,
                        "FAIL",
                        actual_output=actual,
                        reason=f"Expected {case.expected_output!r}, got {actual!r}.",
                    )
                )
                continue

            report.results.append(
                CaseResult(
                    case.name,
                    "PASS",
                    actual_output=actual,
                    reason="Behavior matched contract.",
                )
            )

        return report
