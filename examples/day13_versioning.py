import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_passport.versioning import diff_passports


v1 = {
    "passport": {"version": "1.5"},
    "agent": {"id": "nova", "name": "Nova", "version": "1.0.0"},
    "identity": {"capabilities": ["reasoning", "structured_output"]},
    "behavior": {"input": {"type": "text"}, "output": {"type": "json"}},
    "tools": [{"name": "calculator", "description": "math"}],
    "model": {"interface_version": "1.0", "provider": "any", "model": "any"},
    "runtime": {"compatible": ["native", "portable-host"]},
}

v2 = {
    **v1,
    "agent": {**v1["agent"], "version": "1.1.0"},
    "identity": {"capabilities": ["reasoning", "structured_output", "web_search"]},
    "tools": [
        {"name": "calculator", "description": "math"},
        {"name": "web_search", "description": "search the web"},
    ],
    "model": {"interface_version": "1.0", "provider": "any", "model": "new-model"},
    "runtime": {"compatible": ["native", "portable-host", "langchain"]},
}

result = diff_passports(v1, v2)

print("=== DAY 13: PASSPORT VERSIONING ===")
print(result.pretty())
print("\nSummary:", result.summary)
