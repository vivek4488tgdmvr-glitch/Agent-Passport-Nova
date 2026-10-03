import pytest

signing = pytest.importorskip("agent_passport.passport.signing")


def test_signed_passport_verifies():
    private, public = signing.generate_keypair()
    passport = {
        "passport": {"version": "1.5"},
        "agent": {"id": "nova", "version": "1.0.0"},
    }
    signed = signing.sign_passport(passport, private, "demo-issuer")
    result = signing.verify_signature(signed, public)
    assert result["status"] == "PASS"
    assert result["issuer"] == "demo-issuer"


def test_tampered_passport_is_rejected():
    private, public = signing.generate_keypair()
    passport = {
        "passport": {"version": "1.5"},
        "agent": {"id": "nova", "version": "1.0.0"},
    }
    signed = signing.sign_passport(passport, private, "demo-issuer")
    signed["agent"]["id"] = "evil-nova"
    result = signing.verify_signature(signed, public)
    assert result["status"] == "FAIL"


def test_wrong_public_key_is_rejected():
    private, public = signing.generate_keypair()
    _, wrong_public = signing.generate_keypair()
    signed = signing.sign_passport({"agent": {"id": "nova"}}, private, "issuer")
    result = signing.verify_signature(signed, wrong_public)
    assert result["status"] == "FAIL"
