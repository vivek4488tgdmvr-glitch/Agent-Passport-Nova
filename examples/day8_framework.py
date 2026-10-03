import json

from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.frameworks.bridge import bridge_agent
from agent_passport.migration import build_manifest, migrate_to_framework


agent = Agent(
    agent_id="nova",
    name="Nova",
    version="1.0.0",
    capabilities=["reasoning", "structured_output", "tool_use"],
)

native = NativeRuntime(agent)
external = bridge_agent(agent)

manifest = build_manifest(
    "passport.yaml",
    source_runtime=native.runtime_name,
    target_runtime=external.runtime_name,
)

result = migrate_to_framework(
    native,
    external,
    AgentRequest("Show that Nova can move into another framework host."),
)

print("=== FRAMEWORK MIGRATION ===")
print(json.dumps(result, indent=2))

print("\n=== PASSPORT MANIFEST ===")
print(json.dumps(manifest.to_dict(), indent=2))

print("\n=== RESULT ===")
print("MIGRATION VERIFIED ✓" if result["status"] == "PASS" else "MIGRATION FAILED ✗")
