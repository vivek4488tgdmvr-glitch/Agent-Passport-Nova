import sys
import types

import pytest

from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.frameworks.langchain_adapter import LangChainAdapter
from agent_passport.frameworks.langchain_factory import build_langchain_runnable
from agent_passport.migration import migrate_to_framework


class FakeRunnable:
    def invoke(self, message):
        return f"fake-framework: {message}"


def make_agent():
    return Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )


def test_langchain_adapter_runtime_contract_without_dependency():
    adapter = LangChainAdapter(FakeRunnable(), "nova")
    adapter.initialize()
    response = adapter.run(AgentRequest("hello"))
    adapter.shutdown()

    assert response.content == "fake-framework: hello"
    assert response.metadata["agent_id"] == "nova"
    assert response.metadata["framework"] == "langchain"


def test_langchain_adapter_rejects_invalid_runnable():
    with pytest.raises(TypeError):
        LangChainAdapter(object(), "nova")


def test_langchain_factory_contract_without_optional_dependency(monkeypatch):
    """Exercise the factory contract even when langchain-core is not installed.

    The production integration remains optional. This test supplies a tiny
    RunnableLambda-compatible test double at the import boundary, so the
    factory path itself is always covered and never silently skipped.
    """
    class TestRunnableLambda:
        def __init__(self, fn):
            self._fn = fn

        def invoke(self, message):
            return self._fn(message)

    langchain_core = types.ModuleType("langchain_core")
    runnables = types.ModuleType("langchain_core.runnables")
    runnables.RunnableLambda = TestRunnableLambda
    langchain_core.runnables = runnables
    monkeypatch.setitem(sys.modules, "langchain_core", langchain_core)
    monkeypatch.setitem(sys.modules, "langchain_core.runnables", runnables)

    agent = make_agent()
    runnable = build_langchain_runnable(agent)
    assert hasattr(runnable, "invoke")
    assert runnable.invoke("factory test") == "Nova received: factory test"


def test_migration_contract_works_with_langchain_adapter():
    agent = make_agent()
    adapter = LangChainAdapter(
        FakeRunnable(), "nova"
    )

    # Use a matching native behavior for equivalence.
    class MatchingAgent(Agent):
        def handle(self, request):
            from agent_passport.core import AgentResponse
            return AgentResponse(
                content=f"fake-framework: {request.message}",
                metadata={"agent_id": self.agent_id},
            )

    source_agent = MatchingAgent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning"],
    )

    result = migrate_to_framework(
        NativeRuntime(source_agent),
        adapter,
        AgentRequest("migration"),
    )

    assert result["status"] == "PASS"
