from __future__ import annotations

from agent_passport.model.contract import validate_model_response
from agent_passport.passport.loader import load


def verify_model_contract(agent, passport_path: str) -> dict:
    passport = load(passport_path)

    expected_provider = passport.model.provider
    expected_model = passport.model.model

    response = agent.run("model contract verification")
    response_check = validate_model_response(response)

    provider_ok = expected_provider in {"any", response.provider}
    model_ok = expected_model in {"any", response.model}

    checks = {
        "response_shape": response_check["status"] == "PASS",
        "provider_contract": provider_ok,
        "model_contract": model_ok,
    }

    return {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "provider": response.provider,
        "model": response.model,
        "checks": checks,
    }
