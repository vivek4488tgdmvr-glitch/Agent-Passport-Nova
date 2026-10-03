import json

from agent_passport.adapters.mock_framework import MockFrameworkRuntime
from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.verification import VerificationEngine, compare_runtimes


def multiply(a: int, b: int) -> int:
    return a * b


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

print("=== VERIFICATION ENGINE ===")
engine = VerificationEngine(agent, "passport.yaml")
report = engine.run(NativeRuntime(agent))
print(json.dumps(report, indent=2))

print("\n=== PORTABILITY TEST ===")
portability = compare_runtimes(
    agent,
    [NativeRuntime(agent), MockFrameworkRuntime(agent)],
    AgentRequest("prove portability"),
)
print(json.dumps(portability, indent=2))
