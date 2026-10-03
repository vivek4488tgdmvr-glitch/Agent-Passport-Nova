from agent_passport.adapters.migratable import MigratableRuntime
from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.migration import build_manifest, migrate_agent, verify_migration


def make_agent():
    return Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )


def test_manifest_captures_portability_identity():
    manifest = build_manifest("passport.yaml", "native", "portable-host")

    assert manifest.agent_id == "nova"
    assert manifest.source_runtime == "native"
    assert manifest.target_runtime == "portable-host"
    assert len(manifest.passport_fingerprint) == 64


def test_agent_migrates_between_runtime_hosts():
    agent = make_agent()
    result = migrate_agent(
        NativeRuntime(agent),
        MigratableRuntime(agent),
        AgentRequest("migration proof"),
    )

    assert result["status"] == "PASS"
    assert result["same_agent_identity"] is True
    assert result["same_content"] is True


def test_migration_verification_report():
    agent = make_agent()
    manifest = build_manifest("passport.yaml", "native", "portable-host")
    result = migrate_agent(
        NativeRuntime(agent),
        MigratableRuntime(agent),
        AgentRequest("verify migration"),
    )

    report = verify_migration(manifest, result)
    assert report["status"] == "PASS"
    assert all(report["checks"].values())


def test_migration_detects_identity_change():
    agent = make_agent()
    target = MigratableRuntime(agent)

    source = NativeRuntime(agent)
    source.initialize()
    source_response = source.run(AgentRequest("identity test"))
    source.shutdown()

    agent.agent_id = "tampered"

    target.initialize()
    target_response = target.run(AgentRequest("identity test"))
    target.shutdown()

    assert source_response.metadata["agent_id"] != target_response.metadata["agent_id"]
