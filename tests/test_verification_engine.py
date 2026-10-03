from agent_passport.adapters.mock_framework import MockFrameworkRuntime
from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.verification import VerificationEngine, compare_runtimes


def multiply(a: int, b: int) -> int:
    return a * b


def make_agent() -> Agent:
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )
    agent.register_tool(
        "multiply",
        multiply,
        description="Multiplies two integers.",
        input_schema={"type": "object"},
        output_type="integer",
    )
    return agent


def test_engine_passes_valid_agent():
    agent = make_agent()
    report = VerificationEngine(agent, "passport.yaml").run(
        NativeRuntime(agent)
    )
    assert report["status"] == "PASS"
    assert all(c["status"] == "PASS" for c in report["checks"])


def test_engine_detects_identity_mismatch():
    agent = make_agent()
    agent.agent_id = "tampered-agent"
    report = VerificationEngine(agent, "passport.yaml").run()
    assert report["status"] == "FAIL"
    assert any(c["name"] == "identity_match" and c["status"] == "FAIL"
               for c in report["checks"])


def test_engine_detects_missing_tool():
    agent = make_agent()
    agent.tools.pop("multiply")
    report = VerificationEngine(agent, "passport.yaml").run()
    assert report["status"] == "FAIL"


def test_portability_across_two_runtimes():
    agent = make_agent()
    result = compare_runtimes(
        agent,
        [NativeRuntime(agent), MockFrameworkRuntime(agent)],
        AgentRequest("portable test"),
    )
    assert result["status"] == "PASS"
    assert result["portable"] is True


def test_portability_detects_broken_runtime():
    agent = make_agent()

    class BrokenRuntime:
        runtime_name = "broken"

        def initialize(self):
            pass

        def run(self, request):
            raise RuntimeError("intentional failure")

        def shutdown(self):
            pass

    result = compare_runtimes(
        agent,
        [NativeRuntime(agent), BrokenRuntime()],
        AgentRequest("portable test"),
    )
    assert result["status"] == "FAIL"
