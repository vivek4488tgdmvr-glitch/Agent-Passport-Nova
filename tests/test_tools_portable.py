import pytest

from agent_passport.tools import PortableTool, ToolRegistry, validate_tool_contract
from agent_passport.verification.tool_checks import verify_portable_tools


def calculator():
    return PortableTool(
        tool_id="calculator",
        version="1.0.0",
        description="Adds two numbers.",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["a", "b"],
        },
        output_type="number",
        permissions={"network": False, "filesystem_read": False},
    )


def test_valid_tool_contract():
    result = validate_tool_contract(calculator())
    assert result["status"] == "PASS"


def test_invalid_permission_is_rejected():
    tool = PortableTool(
        "bad", "1.0", "bad tool", {}, "string",
        permissions={"camera": True},
    )
    assert validate_tool_contract(tool)["status"] == "FAIL"


def test_tool_can_bind_to_multiple_runtimes():
    registry = ToolRegistry()
    registry.register(calculator())
    registry.bind("calculator", "native", lambda a, b: a + b)
    registry.bind("calculator", "portable-host", lambda a, b: a + b)

    assert registry.invoke("calculator", "native", 2, 3) == 5
    assert registry.invoke("calculator", "portable-host", 4, 5) == 9
    assert registry.runtimes_for("calculator") == ["native", "portable-host"]


def test_missing_binding_fails():
    registry = ToolRegistry()
    registry.register(calculator())
    with pytest.raises(RuntimeError):
        registry.invoke("calculator", "native", 1, 2)


def test_unknown_tool_cannot_bind():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.bind("missing", "native", lambda: None)


def test_portable_tool_verification():
    result = verify_portable_tools([calculator()])
    assert result["status"] == "PASS"
    assert len(result["tools"]) == 1
