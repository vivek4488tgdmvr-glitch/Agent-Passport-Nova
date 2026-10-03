from pathlib import Path

import pytest
import yaml

from agent_passport.opengap import OpenGAPValidationError, export_opengap_agent, load_agent_yaml, validate_agent_yaml


ROOT = Path(__file__).parents[2]


def test_root_agent_yaml_validates():
    doc = validate_agent_yaml(ROOT / "agent.yaml")
    assert doc.spec == "0.1.0"
    assert doc.agent["id"] == "nova"
    assert doc.frameworks.targets == ["openai-sdk", "crewai", "claude-code", "lyzr"]


def test_root_entrypoint_is_required():
    with pytest.raises(OpenGAPValidationError, match="root-level agent.yaml"):
        load_agent_yaml(ROOT / "passport.yaml")


def test_invalid_spec_is_rejected(tmp_path):
    path = tmp_path / "agent.yaml"
    path.write_text("spec: '9.9.9'\nagent: {}\nbehavior: {input: {type: text}, output: {type: json}}\n", encoding="utf-8")
    with pytest.raises(OpenGAPValidationError):
        validate_agent_yaml(path)


def test_unknown_root_field_is_rejected(tmp_path):
    path = tmp_path / "agent.yaml"
    raw = yaml.safe_load((ROOT / "agent.yaml").read_text(encoding="utf-8"))
    raw["unexpected"] = True
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(OpenGAPValidationError):
        validate_agent_yaml(path)


def test_export_from_passport_round_trips(tmp_path):
    output = tmp_path / "agent.yaml"
    export_opengap_agent(ROOT / "passport.yaml", output)
    doc = validate_agent_yaml(output)
    assert doc.agent["id"] == "nova"
    assert doc.tools[0].name == "multiply"
    assert "openai-sdk" in doc.frameworks.targets


def test_missing_agent_field_is_rejected(tmp_path):
    raw = yaml.safe_load((ROOT / "agent.yaml").read_text(encoding="utf-8"))
    del raw["agent"]["version"]
    path = tmp_path / "agent.yaml"
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")
    with pytest.raises(OpenGAPValidationError, match="version"):
        validate_agent_yaml(path)
