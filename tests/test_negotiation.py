from agent_passport.negotiation import negotiate, require_compatible
import pytest


def passport(capabilities):
    return {
        "agent": {"id": "nova", "version": "1.0.0"},
        "identity": {"capabilities": capabilities},
    }


def test_all_requirements_satisfied():
    result = negotiate(
        passport(["reasoning", "structured_output"]),
        {"capabilities": ["reasoning", "structured_output", "tool_use"]},
    )
    assert result.compatible
    assert result.missing == []


def test_missing_capability_blocks_migration():
    result = negotiate(
        passport(["reasoning", "tool_use"]),
        {"capabilities": ["reasoning"]},
    )
    assert not result.compatible
    assert result.missing == ["tool_use"]


def test_multiple_missing_capabilities_are_reported():
    result = negotiate(
        passport(["reasoning", "tool_use", "web_search"]),
        {"capabilities": ["reasoning"]},
    )
    assert result.missing == ["tool_use", "web_search"]


def test_conflict_blocks_even_when_capabilities_exist():
    result = negotiate(
        passport(["reasoning"]),
        {"capabilities": ["reasoning"]},
        conflicts=["network policy forbids external access"],
    )
    assert not result.compatible
    assert result.conflicts == ["network policy forbids external access"]


def test_require_compatible_raises_on_failure():
    with pytest.raises(RuntimeError):
        require_compatible(passport(["tool_use"]), {"capabilities": []})


def test_empty_requirements_are_compatible():
    result = negotiate(passport([]), {"capabilities": []})
    assert result.compatible
