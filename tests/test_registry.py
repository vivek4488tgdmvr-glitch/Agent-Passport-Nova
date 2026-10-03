import json

from agent_passport.registry import PassportRegistry, RegistryStatus


def passport(version="1.0.0"):
    return {
        "passport": {"version": "1.5"},
        "agent": {"id": "nova", "name": "Nova", "version": version},
        "identity": {"capabilities": ["reasoning"]},
    }


def test_register_list_and_verify(tmp_path):
    registry = PassportRegistry(tmp_path / "registry.json")
    entry = registry.register(passport(), issuer="demo")
    assert entry.agent_id == "nova"
    assert entry.status == RegistryStatus.ACTIVE
    assert len(registry.list()) == 1
    assert registry.verify_registered(entry.passport_id)["status"] == "PASS"


def test_revoke_blocks_verification(tmp_path):
    registry = PassportRegistry(tmp_path / "registry.json")
    entry = registry.register(passport())
    registry.revoke(entry.passport_id)
    assert registry.verify_registered(entry.passport_id)["status"] == "FAIL"
    assert registry.list() == []


def test_multiple_versions_are_discoverable(tmp_path):
    registry = PassportRegistry(tmp_path / "registry.json")
    registry.register(passport("1.0.0"))
    registry.register(passport("1.1.0"))
    versions = [e.version for e in registry.find_agent("nova")]
    assert versions == ["1.0.0", "1.1.0"]


def test_modified_registered_content_is_detected(tmp_path):
    registry = PassportRegistry(tmp_path / "registry.json")
    entry = registry.register(passport())
    raw = json.loads((tmp_path / "registry.json").read_text())
    raw[0]["passport"]["agent"]["name"] = "Tampered"
    (tmp_path / "registry.json").write_text(json.dumps(raw))
    assert registry.verify_registered(entry.passport_id)["status"] == "FAIL"
