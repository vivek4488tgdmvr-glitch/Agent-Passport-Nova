import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.negotiation import negotiate


passport = {
    "agent": {"id": "nova", "version": "1.1.0"},
    "identity": {
        "capabilities": ["reasoning", "structured_output", "tool_use", "web_search"]
    },
}

capable_runtime = {
    "name": "portable-host",
    "capabilities": ["reasoning", "structured_output", "tool_use", "web_search"],
}

limited_runtime = {
    "name": "minimal-runtime",
    "capabilities": ["reasoning", "structured_output"],
}

print("=== DAY 14: CAPABILITY NEGOTIATION ===")

print("\n[1] Capable runtime")
result = negotiate(passport, capable_runtime)
print(result.pretty())

print("\n[2] Limited runtime")
result = negotiate(passport, limited_runtime)
print(result.pretty())
