import pytest

from agent_passport.core import Agent
from agent_passport.visas import (
    ClaudeCodeVisaAdapter,
    CrewAIVisaAdapter,
    LyzrVisaAdapter,
    OpenAISDKVisaAdapter,
    export_all_visas,
    export_framework,
    verify_export,
)


def make_agent():
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )
    agent.register_tool("multiply", lambda a, b: a * b)
    return agent


@pytest.mark.parametrize(
    "adapter_cls, framework",
    [
        (OpenAISDKVisaAdapter, "openai-sdk"),
        (CrewAIVisaAdapter, "crewai"),
        (ClaudeCodeVisaAdapter, "claude-code"),
        (LyzrVisaAdapter, "lyzr"),
    ],
)
def test_each_framework_export_issues_a_valid_visa(adapter_cls, framework):
    export = adapter_cls().export(make_agent())
    assert export.framework == framework
    assert export.visa.status.value == "ISSUED"
    assert verify_export(export)
    assert export.artifact["agent"]["id"] == "nova"
    assert export.artifact["tools"] == ["multiply"]


def test_all_four_visas_export_together():
    exports = export_all_visas(make_agent())
    assert list(exports) == ["openai-sdk", "crewai", "claude-code", "lyzr"]
    assert all(verify_export(item) for item in exports.values())
    assert len({item.visa.visa_id for item in exports.values()}) == 4


def test_registry_lookup_is_case_insensitive():
    export = export_framework(make_agent(), " CrewAI ")
    assert export.framework == "crewai"
    assert verify_export(export)


def test_unknown_framework_is_rejected():
    with pytest.raises(KeyError):
        export_framework(make_agent(), "unknown-framework")


def test_invalid_agent_is_rejected_at_visa_boundary():
    invalid = Agent(agent_id="bad/id", name="Nova", version="1.0.0")
    with pytest.raises(ValueError):
        OpenAISDKVisaAdapter().export(invalid)
