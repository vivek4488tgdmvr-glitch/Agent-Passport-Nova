import json

from agent_passport.adapters.model_runtime import ModelRuntime
from agent_passport.core.contracts import AgentRequest
from agent_passport.core.llm_agent import LLMBackedAgent
from agent_passport.model import MockModelProvider


agent = LLMBackedAgent(
    agent_id="nova",
    name="Nova",
    version="0.5.0",
    model=MockModelProvider(),
    system_prompt="You are Nova, a portable AI agent.",
    capabilities=["reasoning", "structured_output", "tool_use"],
)

print("=== PORTABLE AGENT ===")
print(json.dumps(agent.describe(), indent=2))

runtime = ModelRuntime(agent)
runtime.initialize()

print("\n=== MODEL RESPONSE ===")
response = runtime.run(AgentRequest("Explain why portability matters."))
print(json.dumps({
    "content": response.content,
    "provider": response.metadata["provider"],
    "model": response.metadata["model"],
}, indent=2))

runtime.shutdown()
