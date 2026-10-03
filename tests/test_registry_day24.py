from __future__ import annotations

import json

import pytest

from agent_passport.passport.signing import generate_keypair, sign_passport
from agent_passport.registry import PassportRegistry


def base(version="1.0.0"):
    return {
        "passport": {"version": "1.5"},
        "agent": {"id": "nova", "name": "Nova", "version": version},
        "identity": {"capabilities": ["reasoning"]},
    }


def test_publish_requires_valid_signature(tmp_path):
    private, public = generate_keypair()
    signed = sign_passport(base(), private, "issuer")
    r = PassportRegistry(tmp_path / "registry.json")
    e = r.publish(signed, public_key=public)
    assert e.public_key == public
    assert r.retrieve_verified(e.passport_id)["status"] == "PASS"


def test_publish_rejects_tampered_signed_passport(tmp_path):
    private, public = generate_keypair()
    signed = sign_passport(base(), private, "issuer")
    signed["identity"]["capabilities"].append("shell")
    with pytest.raises(ValueError):
        PassportRegistry(tmp_path / "registry.json").publish(signed, public_key=public)


def test_latest_and_versions_exclude_revoked_by_default(tmp_path):
    private, public = generate_keypair()
    r = PassportRegistry(tmp_path / "registry.json")
    e1 = r.publish(sign_passport(base("1.0.0"), private, "issuer"), public_key=public)
    e2 = r.publish(sign_passport(base("1.1.0"), private, "issuer"), public_key=public)
    assert r.versions("nova") == ["1.0.0", "1.1.0"]
    assert r.latest("nova").passport_id == e2.passport_id
    r.revoke(e2.passport_id)
    assert r.latest("nova").passport_id == e1.passport_id


def test_verified_retrieval_fails_after_registry_tamper(tmp_path):
    private, public = generate_keypair()
    r = PassportRegistry(tmp_path / "registry.json")
    e = r.publish(sign_passport(base(), private, "issuer"), public_key=public)
    raw = json.loads((tmp_path / "registry.json").read_text())
    raw[0]["passport"]["agent"]["name"] = "Tampered"
    (tmp_path / "registry.json").write_text(json.dumps(raw))
    result = r.retrieve_verified(e.passport_id)
    assert result["status"] == "FAIL"


def test_signature_is_checked_during_retrieval(tmp_path):
    private, public = generate_keypair()
    wrong_private, wrong_public = generate_keypair()
    signed = sign_passport(base(), private, "issuer")
    r = PassportRegistry(tmp_path / "registry.json")
    e = r.register(signed, public_key=wrong_public)
    result = r.retrieve_verified(e.passport_id)
    assert result["status"] == "FAIL"
