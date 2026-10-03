from agent_passport.verification.validator import load_passport


def test_passport_loads():
    passport = load_passport("passport.yaml")

    assert passport.agent.id == "nova"
    assert passport.agent.name == "Nova"
    assert "reasoning" in passport.identity.capabilities
    assert "native" in passport.runtime.compatible
