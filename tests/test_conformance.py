import pytest

from agent_passport.conformance import BehaviorCase, ConformanceRunner
from agent_passport.verification.behavior_conformance import (
    cases_from_behavior_contract,
    verify_behavior_conformance,
)


def test_matching_output_passes():
    report = ConformanceRunner(lambda x: x * 2).run([
        BehaviorCase("double", 3, expected_output=6),
    ])
    assert report.status == "PASS"
    assert report.passed == 1
    assert report.failed == 0


def test_mismatched_output_fails():
    report = ConformanceRunner(lambda x: x * 2).run([
        BehaviorCase("double", 3, expected_output=7),
    ])
    assert report.status == "FAIL"
    assert report.failed == 1


def test_output_type_is_checked():
    report = ConformanceRunner(lambda x: str(x)).run([
        BehaviorCase("stringify", 3, expected_output_type="int"),
    ])
    assert report.status == "FAIL"


def test_expected_exception_passes():
    def handler(_):
        raise ValueError("bad input")

    report = ConformanceRunner(handler).run([
        BehaviorCase("bad-input", "x", expected_error="ValueError"),
    ])
    assert report.status == "PASS"


def test_unexpected_exception_fails():
    def handler(_):
        raise RuntimeError("boom")

    report = ConformanceRunner(handler).run([
        BehaviorCase("unexpected", "x", expected_output="ok"),
    ])
    assert report.status == "FAIL"
    assert report.results[0].error == "RuntimeError"


def test_contract_cases_are_parsed():
    contract = {
        "input": {"type": "text"},
        "output": {"type": "json"},
        "test_cases": [
            {"name": "hello", "input": "hello", "expected_output": {"ok": True}},
            {"name": "type", "input": "x", "expected_output_type": "dict"},
        ],
    }
    cases = cases_from_behavior_contract(contract)
    assert len(cases) == 2
    assert cases[0].name == "hello"


def test_contract_conformance():
    contract = {
        "test_cases": [
            {"name": "echo", "input": "hello", "expected_output": "hello"},
        ]
    }
    result = verify_behavior_conformance(lambda x: x, contract)
    assert result["status"] == "PASS"
    assert result["passed"] == 1


def test_empty_contract_is_skipped():
    result = verify_behavior_conformance(lambda x: x, {})
    assert result["status"] == "SKIPPED"
