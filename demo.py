"""Submission-friendly Agent Passport demo.

Works without API keys or optional framework packages. If langchain-core is
installed, it additionally demonstrates the real LangChain adapter.
"""

import json

from agent_passport.adapters.native import NativeRuntime
from agent_passport.core import Agent, AgentRequest
from agent_passport.migration import build_manifest, migrate_to_framework
from agent_passport.passport import fingerprint, load
from agent_passport.verification import VerificationEngine


def build_agent():
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )
    agent.register_tool(
        "multiply",
        lambda a, b: a * b,
        description="Multiplies two integers.",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
        output_type="integer",
    )
    return agent


def main():
    passport = load("passport.yaml")
    agent = build_agent()
    native = NativeRuntime(agent)

    print("\n=== AGENT PASSPORT DEMO ===")
    print(f"Agent: {passport.agent.name} v{passport.agent.version}")
    print(f"Passport fingerprint: {fingerprint(passport)[:16]}...")

    verification = VerificationEngine(agent, "passport.yaml").run(native)
    print(f"\nBaseline verification: {verification['status']}")

    try:
        from agent_passport.frameworks.langchain_factory import build_langchain_runnable
        from agent_passport.frameworks.langchain_adapter import LangChainAdapter

        runnable = build_langchain_runnable(agent)
        target = LangChainAdapter(runnable, agent.agent_id)

        manifest = build_manifest(
            "passport.yaml", native.runtime_name, target.runtime_name
        )
        migration = migrate_to_framework(
            native,
            target,
            AgentRequest("Prove that Nova can travel."),
        )

        print("\nFramework: LangChain")
        print(f"Migration: {migration['status']}")
        print(f"Identity preserved: {migration['identity_preserved']}")
        print(f"Behavior preserved: {migration['behavior_preserved']}")
        print(f"Passport fingerprint: {manifest.passport_fingerprint[:16]}...")
    except RuntimeError as exc:
        print("\nFramework integration: optional")
        print(str(exc))
        print("Core Passport verification remains available.")

    print("\n=== RESULT ===")
    if verification["status"] == "PASS":
        print("PASSPORT VERIFIED ✓")
    else:
        print("PASSPORT VERIFICATION FAILED ✗")


if __name__ == "__main__":
    main()
