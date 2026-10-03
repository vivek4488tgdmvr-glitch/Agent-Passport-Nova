import json

from agent_passport.passport import export_passport, fingerprint, load, verify


def test_yaml_load_and_fingerprint():
    passport = load("passport.yaml")
    assert passport.agent.id == "nova"
    assert len(fingerprint(passport)) == 64


def test_yaml_to_json_round_trip(tmp_path):
    passport = load("passport.yaml")
    output = tmp_path / "passport.json"

    export_passport(passport, output)
    restored = load(output)

    assert restored == passport


def test_verification_report_passes():
    report = verify("passport.yaml")
    assert report["status"] == "PASS"
    assert all(check["status"] == "PASS" for check in report["checks"])


def test_fingerprint_is_stable(tmp_path):
    passport = load("passport.yaml")
    json_path = tmp_path / "passport.json"
    export_passport(passport, json_path)

    assert fingerprint(passport) == fingerprint(load(json_path))


def test_cli_modules_are_importable():
    from agent_passport.cli import main
    assert callable(main)
