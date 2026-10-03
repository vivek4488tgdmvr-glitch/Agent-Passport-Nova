import json

from agent_passport.adapters.migratable import MigratableRuntime
from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.migration import build_manifest, migrate_agent, verify_migration


agent = Agent(
    agent_id="nova",
    name="Nova",
    version="1.0.0",
    capabilities=["reasoning", "structured_output", "tool_use"],
)

source = NativeRuntime(agent)
target = MigratableRuntime(agent)

manifest = build_manifest(
    "passport.yaml",
    source_runtime=source.runtime_name,
    target_runtime=target.runtime_name,
)

migration = migrate_agent(
    source,
    target,
    AgentRequest("Demonstrate that Nova can travel."),
)

report = verify_migration(manifest, migration)

print("=== MIGRATION MANIFEST ===")
print(json.dumps(manifest.to_dict(), indent=2))

print("\n=== SOURCE → TARGET ===")
print(json.dumps(migration, indent=2))

print("\n=== MIGRATION VERIFICATION ===")
print(json.dumps(report, indent=2))
