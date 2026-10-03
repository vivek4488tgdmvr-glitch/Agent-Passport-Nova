import copy

from agent_passport.passport.evidence import evidence_hash, sign_evidence, verify_evidence
from agent_passport.passport.signing import generate_keypair


def sample():
    return {
        "status": "PASS",
        "total_steps": 2,
        "passed": 2,
        "failed": 0,
        "steps": [
            {"step": "IDENTITY", "status": "PASS", "detail": "Nova"},
            {"step": "TRAVEL", "status": "PASS", "detail": "complete"},
        ],
    }


def test_evidence_hash_is_deterministic():
    assert evidence_hash(sample()) == evidence_hash(copy.deepcopy(sample()))


def test_signed_evidence_verifies_and_binds_passport():
    private, public = generate_keypair()
    signed = sign_evidence(sample(), "abc123", private, "demo-issuer")
    assert signed["cryptographic_evidence"]["public_key"]
    result = verify_evidence(signed, "abc123")
    assert result["status"] == "PASS"
    assert result["passport_fingerprint"] == "abc123"
    assert public  # public key remains independently available for comparison/inspection


def test_tampered_evidence_is_rejected():
    private, _ = generate_keypair()
    signed = sign_evidence(sample(), "abc123", private, "demo-issuer")
    signed["steps"][0]["detail"] = "TAMPERED"
    assert verify_evidence(signed, "abc123")["status"] == "FAIL"


def test_wrong_passport_fingerprint_is_rejected():
    private, _ = generate_keypair()
    signed = sign_evidence(sample(), "abc123", private, "demo-issuer")
    result = verify_evidence(signed, "different-passport")
    assert result["status"] == "FAIL"
    assert "different Passport fingerprint" in result["reason"]
