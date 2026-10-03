import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.tools import PortableTool, ToolRegistry
from agent_passport.verification.tool_checks import verify_portable_tools


calculator = PortableTool(
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
    permissions={"network": False, "filesystem_write": False},
)

registry = ToolRegistry()
registry.register(calculator)

# Two different runtime implementations satisfy the same portable contract.
registry.bind("calculator", "native", lambda a, b: a + b)
registry.bind("calculator", "portable-host", lambda a, b: a + b)

print("=== DAY 15: PORTABLE TOOLS ===")
print("Contract verification:", verify_portable_tools([calculator])["status"], "✓")

print("\nNative runtime:")
print("calculator(2, 3) =", registry.invoke("calculator", "native", 2, 3))

print("\nPortable host:")
print("calculator(2, 3) =", registry.invoke("calculator", "portable-host", 2, 3))

print("\nSame portable contract ✓")
print("Different runtime bindings ✓")
print("Tool can travel with the agent ✓")
