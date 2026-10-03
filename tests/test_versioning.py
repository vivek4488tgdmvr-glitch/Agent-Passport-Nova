from agent_passport.versioning import diff_passports


def base(version="1.0.0"):
    return {
        "passport": {"version": "1.5"},
        "agent": {"id": "nova", "name": "Nova", "version": version},
        "identity": {"capabilities": ["reasoning", "structured_output"]},
        "behavior": {"input": {"type": "text"}, "output": {"type": "json"}},
        "tools": [{"name": "calculator", "description": "math"}],
        "model": {"interface_version": "1.0", "provider": "any", "model": "any"},
    }


def test_identical_passports_have_no_changes():
    result = diff_passports(base(), base())
    assert not result.changed
    assert result.summary == {"added": 0, "removed": 0, "modified": 0}


def test_capability_addition_is_detected():
    newer = base("1.1.0")
    newer["identity"]["capabilities"].append("web_search")
    result = diff_passports(base(), newer)
    assert result.summary["added"] == 1
    assert any(c.path == "identity.capabilities[]" for c in result.changes)


def test_tool_removal_is_detected():
    newer = base("1.1.0")
    newer["tools"] = []
    result = diff_passports(base(), newer)
    assert result.summary["removed"] == 1


def test_model_change_is_modified():
    newer = base("2.0.0")
    newer["model"]["model"] = "new-model"
    result = diff_passports(base(), newer)
    assert result.summary["modified"] == 1
    assert any(c.path == "model.model" for c in result.changes)


def test_nested_behavior_change_is_detected():
    newer = base("1.1.0")
    newer["behavior"]["output"]["type"] = "text"
    result = diff_passports(base(), newer)
    assert result.summary["modified"] == 1
    assert any(c.path == "behavior.output.type" for c in result.changes)
