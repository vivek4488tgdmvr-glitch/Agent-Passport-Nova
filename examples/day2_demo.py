from agent_passport.core import Agent, AgentRequest
from agent_passport.adapters.native import NativeRuntime
from agent_passport.adapters.mock_framework import MockFrameworkRuntime
from agent_passport.verification.validator import verify_passport


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

request = AgentRequest("Demonstrate portability.")

print("=== AGENT ===")
print(agent.describe())

print("\n=== TOOL CONTRACT ===")
print(agent.tool_contracts())

print("\n=== TOOL EXECUTION ===")
print("multiply(6, 7) =", agent.execute_tool("multiply", a=6, b=7))

print("\n=== RUNTIME A: NATIVE ===")
runtime_a = NativeRuntime(agent)
runtime_a.initialize()
print(runtime_a.run(request))
runtime_a.shutdown()

print("\n=== RUNTIME B: MOCK FRAMEWORK ===")
runtime_b = MockFrameworkRuntime(agent)
runtime_b.initialize()
print(runtime_b.run(request))
runtime_b.shutdown()

print("\n=== PASSPORT ===")
print(verify_passport("passport.yaml"))
