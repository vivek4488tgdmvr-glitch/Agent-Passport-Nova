from agent_passport.passport import load


def test_passport_declares_provider_independent_model():
    passport = load("passport.yaml")

    assert passport.model.interface_version == "1.0"
    assert passport.model.provider == "any"
    assert passport.model.model == "any"
    assert "model-runtime" in passport.runtime.compatible
