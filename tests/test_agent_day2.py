from agent_passport.core import Agent, AgentRequest
from agent_passport.adapters.native import NativeRuntime
from agent_passport.adapters.mock_framework import MockFrameworkRuntime


def add(a: int, b: int) -> int:
    return a + b


def make_agent() -> Agent:
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output"],
    )
    agent.register_tool(
        "add",
        add,
        description="Adds two integers.",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
        output_type="integer",
    )
    return agent


def test_tool_contract_and_execution():
    agent = make_agent()
    assert agent.execute_tool("add", a=2, b=3) == 5
    assert agent.tool_contracts()[0]["name"] == "add"


def test_same_agent_runs_in_two_runtimes():
    agent = make_agent()
    request = AgentRequest("Hello Nova")

    native = NativeRuntime(agent)
    native.initialize()
    native_response = native.run(request)
    native.shutdown()

    other = MockFrameworkRuntime(agent)
    other.initialize()
    other_response = other.run(request)
    other.shutdown()

    assert native_response.content == other_response.content
    assert native_response.metadata["agent_id"] == other_response.metadata["agent_id"]
    assert other_response.metadata["runtime"] == "mock-framework"
