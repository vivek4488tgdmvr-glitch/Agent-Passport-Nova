from agent_passport.core.llm_agent import LLMBackedAgent
from agent_passport.model import (
    MockModelProvider,
    OpenAICompatibleProvider,
    build_model_contract,
    validate_model_response,
)
from agent_passport.verification import verify_model_contract


def test_openai_compatible_provider_has_standard_interface():
    provider = OpenAICompatibleProvider(
        model_name="demo-model",
        base_url="https://example.test/v1",
        api_key="test-key",
    )
    assert provider.provider_name == "openai-compatible"
    assert provider.model_name == "demo-model"
    assert callable(provider.generate)


def test_model_response_contract():
    response = MockModelProvider().generate([])
    result = validate_model_response(response)
    assert result["status"] == "PASS"


def test_model_contract_can_be_built_without_provider_sdk():
    contract = build_model_contract(MockModelProvider())
    assert contract == {
        "interface_version": "1.0",
        "provider": "mock",
        "model": "nova-demo-1",
    }


def test_passport_model_verification():
    agent = LLMBackedAgent(
        agent_id="nova",
        name="Nova",
        version="0.5.0",
        model=MockModelProvider(),
    )
    report = verify_model_contract(agent, "passport.yaml")
    assert report["status"] == "PASS"
    assert report["checks"]["response_shape"] is True
    assert report["checks"]["provider_contract"] is True


def test_real_provider_does_not_require_sdk_at_import_time():
    provider = OpenAICompatibleProvider(
        model_name="test",
        base_url="https://example.test/v1",
        api_key=None,
    )
    try:
        provider.generate([])
    except RuntimeError as exc:
        assert "AGENT_API_KEY" in str(exc)
