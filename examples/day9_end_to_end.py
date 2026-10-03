import json

from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.frameworks.langchain_adapter import LangChainAdapter
from agent_passport.frameworks.langchain_factory import build_langchain_runnable
from agent_passport.migration import (
    build_manifest,
    migrate_to_framework,
)
from agent_passport.passport import fingerprint, load
from agent_passport.verification import VerificationEngine


def main():
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )

    passport = load("passport.yaml")
    native = NativeRuntime(agent)

    print("╔══════════════════════════════════════════╗")
    print("║        AGENT PASSPORT — DAY 9           ║")
    print("╚══════════════════════════════════════════╝")

    print("\n[1] PASSPORT")
    print("Agent:", passport.agent.name)
    print("Fingerprint:", fingerprint(passport))

    print("\n[2] BASELINE VERIFICATION")
    verification = VerificationEngine(agent, "passport.yaml").run(native)
    print(json.dumps(verification, indent=2))

    try:
        runnable = build_langchain_runnable(agent)
    except RuntimeError as exc:
        print("\n[3] LANGCHAIN")
        print("Optional integration not installed:", exc)
        print("Install with: pip install langchain-core")
        print("\nThe adapter itself is tested without requiring the dependency.")
        return

    langchain_runtime = LangChainAdapter(runnable, agent.agent_id)

    print("\n[3] FRAMEWORK MIGRATION")
    manifest = build_manifest(
        "passport.yaml",
        native.runtime_name,
        langchain_runtime.runtime_name,
    )
    migration = migrate_to_framework(
        native,
        langchain_runtime,
        AgentRequest("Prove that Nova survives framework migration."),
    )

    print(json.dumps({
        "manifest": manifest.to_dict(),
        "migration": migration,
    }, indent=2))

    print("\n[4] FINAL RESULT")
    if (
        verification["status"] == "PASS"
        and migration["status"] == "PASS"
    ):
        print("✓ PASSPORT VERIFIED")
        print("✓ FRAMEWORK MIGRATION VERIFIED")
        print("✓ IDENTITY PRESERVED")
        print("✓ BEHAVIOR PRESERVED")
        print("\nAGENT CAN TRAVEL ✓")
    else:
        print("MIGRATION FAILED ✗")


if __name__ == "__main__":
    main()
