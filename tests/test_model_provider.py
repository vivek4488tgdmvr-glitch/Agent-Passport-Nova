from agent_passport.model import ModelMessage, MockModelProvider
from agent_passport.core.llm_agent import LLMBackedAgent
from agent_passport.adapters.model_runtime import ModelRuntime
from agent_passport.core.contracts import AgentRequest


def test_provider_contract():
    provider = MockModelProvider()
    response = provider.generate([
        ModelMessage(role="user", content="hello")
    ])

    assert response.provider == "mock"
    assert response.model == "nova-demo-1"
    assert response.content == "Model response: hello"


def test_agent_is_provider_independent():
    agent = LLMBackedAgent(
        agent_id="nova",
        name="Nova",
        version="0.5.0",
        model=MockModelProvider(),
        capabilities=["reasoning", "tool_use"],
    )

    response = agent.run("portable intelligence")
    assert response.content == "Model response: portable intelligence"
    assert response.provider == "mock"


def test_model_runtime_uses_same_runtime_contract():
    agent = LLMBackedAgent(
        agent_id="nova",
        name="Nova",
        version="0.5.0",
        model=MockModelProvider(),
    )

    runtime = ModelRuntime(agent)
    runtime.initialize()
    response = runtime.run(AgentRequest("runtime test"))
    runtime.shutdown()

    assert response.content == "Model response: runtime test"
    assert response.metadata["agent_id"] == "nova"
    assert response.metadata["provider"] == "mock"


def test_provider_swap_does_not_change_agent_api():
    class SecondMockProvider(MockModelProvider):
        provider_name = "second-mock"
        model_name = "second-model"

    agent = LLMBackedAgent(
        agent_id="nova",
        name="Nova",
        version="0.5.0",
        model=SecondMockProvider(),
    )

    response = agent.run("same interface")
    assert response.provider == "second-mock"
    assert response.model == "second-model"
