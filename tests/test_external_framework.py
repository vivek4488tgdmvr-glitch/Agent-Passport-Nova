from agent_passport.core import Agent, AgentRequest
from agent_passport.frameworks.bridge import bridge_agent
from agent_passport.frameworks.external import ExternalFrameworkAdapter, FrameworkAgent
from agent_passport.migration import migrate_to_framework
from agent_passport.adapters.native import NativeRuntime


def make_agent():
    return Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )


def test_framework_agent_has_independent_interface():
    framework_agent = FrameworkAgent(
        name="Nova",
        instructions="Test",
        handler=lambda message: f"Framework: {message}",
    )
    assert framework_agent.invoke("hello") == "Framework: hello"


def test_adapter_exposes_runtime_contract():
    framework_agent = FrameworkAgent(
        name="Nova",
        instructions="Test",
        handler=lambda message: f"Framework: {message}",
    )
    adapter = ExternalFrameworkAdapter(framework_agent, "nova")
    adapter.initialize()
    response = adapter.run(AgentRequest("hello"))
    adapter.shutdown()

    assert response.metadata["agent_id"] == "nova"
    assert response.metadata["framework"] == "external-framework"


def test_portable_agent_can_be_bridged():
    agent = make_agent()
    adapter = bridge_agent(agent)

    adapter.initialize()
    response = adapter.run(AgentRequest("bridge test"))
    adapter.shutdown()

    assert response.content == "Nova received: bridge test"
    assert response.metadata["agent_id"] == "nova"


def test_migration_to_external_framework():
    agent = make_agent()
    framework_runtime = bridge_agent(agent)

    result = migrate_to_framework(
        NativeRuntime(agent),
        framework_runtime,
        AgentRequest("same behavior"),
    )

    assert result["status"] == "PASS"
    assert result["identity_preserved"] is True
    assert result["behavior_preserved"] is True
