import json
import os

from agent_passport.core.llm_agent import LLMBackedAgent
from agent_passport.model import (
    MockModelProvider,
    OpenAICompatibleProvider,
)
from agent_passport.verification import verify_model_contract


def make_provider():
    """Use a real OpenAI-compatible endpoint only when configured.

    Otherwise return the deterministic mock so the demo works offline.
    """
    if os.getenv("AGENT_API_KEY"):
        return OpenAICompatibleProvider()
    return MockModelProvider()


provider = make_provider()

agent = LLMBackedAgent(
    agent_id="nova",
    name="Nova",
    version="0.5.0",
    model=provider,
    capabilities=["reasoning", "structured_output", "tool_use"],
)

response = agent.run("Give one sentence explaining agent portability.")

print("=== PROVIDER ===")
print(json.dumps({
    "provider": response.provider,
    "model": response.model,
}, indent=2))

print("\n=== RESPONSE ===")
print(response.content)

print("\n=== PASSPORT MODEL CHECK ===")
print(json.dumps(verify_model_contract(agent, "passport.yaml"), indent=2))
