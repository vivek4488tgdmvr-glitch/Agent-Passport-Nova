import json

import pytest

from agent_passport.security import SecureKeyStore
from agent_passport.passport.signing import sign_passport, verify_signature


def test_keystore_encrypts_private_key_at_rest(tmp_path):
    path = tmp_path / "signing.keystore.json"
    result = SecureKeyStore.create(path, "correct horse battery staple", issuer="nova")
    raw = path.read_text()
    assert result["public_key"]
    assert result["public_key"] in raw
    assert "private_key" not in raw
    assert "Ed25519PrivateKey" not in raw
    assert SecureKeyStore(path).metadata()["algorithm"] == "AES-256-GCM"


def test_keystore_requires_correct_password(tmp_path):
    path = tmp_path / "key.json"
    SecureKeyStore.create(path, "right")
    store = SecureKeyStore(path)
    with pytest.raises(ValueError, match="authentication failed"):
        store.load_private_key("wrong")
    assert len(store.load_private_key("right")) > 20


def test_keystore_private_key_can_sign_and_public_key_verifies(tmp_path):
    path = tmp_path / "key.json"
    SecureKeyStore.create(path, "secret", issuer="test")
    store = SecureKeyStore(path)
    passport = {"passport": {"version": "1.0"}, "agent": {"id": "nova"}}
    signed = sign_passport(passport, store.load_private_key("secret"), "test")
    result = verify_signature(signed, store.public_key())
    assert result["status"] == "PASS"


def test_keystore_rotation_authenticates_old_password(tmp_path):
    path = tmp_path / "key.json"
    SecureKeyStore.create(path, "old")
    store = SecureKeyStore(path)
    old_public = store.public_key()
    result = store.rotate("old", new_password="new")
    assert result["public_key"] != old_public
    with pytest.raises(ValueError):
        store.load_private_key("old")
    assert store.load_private_key("new")


def test_keystore_rotation_rejects_wrong_password_without_replacing(tmp_path):
    path = tmp_path / "key.json"
    SecureKeyStore.create(path, "old")
    store = SecureKeyStore(path)
    old_public = store.public_key()
    with pytest.raises(ValueError):
        store.rotate("wrong")
    assert store.public_key() == old_public
