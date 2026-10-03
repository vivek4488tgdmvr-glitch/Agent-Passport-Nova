from __future__ import annotations

from typing import Any, Callable

from ..conformance import BehaviorCase, ConformanceRunner


def cases_from_behavior_contract(contract: dict[str, Any]) -> list[BehaviorCase]:
    """Convert an optional behavior.test_cases section into executable cases."""
    cases = contract.get("test_cases", [])
    result = []

    for item in cases:
        result.append(
            BehaviorCase(
                name=item["name"],
                input=item.get("input"),
                expected_output=item.get("expected_output"),
                expected_output_type=item.get("expected_output_type"),
                expected_error=item.get("expected_error"),
            )
        )
    return result


def verify_behavior_conformance(
    handler: Callable[[Any], Any],
    contract: dict[str, Any],
):
    cases = cases_from_behavior_contract(contract)
    if not cases:
        return {
            "status": "SKIPPED",
            "reason": "No executable behavior test cases declared.",
        }

    return ConformanceRunner(handler).run(cases).to_dict()
