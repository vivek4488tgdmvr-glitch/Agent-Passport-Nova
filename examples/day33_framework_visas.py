from agent_passport.core import Agent
from agent_passport.visas import export_all_visas, verify_export


def main():
    agent = Agent(
        agent_id="nova",
        name="Nova",
        version="1.0.0",
        capabilities=["reasoning", "structured_output", "tool_use"],
    )
    exports = export_all_visas(agent)

    print("=== DAY 33: FRAMEWORK VISAS ===")
    print()
    passed = 0
    for name, export in exports.items():
        ok = verify_export(export)
        passed += ok
        print(f"{name:12} → {'VISA ISSUED ✓' if ok else 'REJECTED ✗'}")
        print(f"  visa: {export.visa.visa_id}")

    print()
    print(f"FRAMEWORK VISAS: {passed}/{len(exports)} PASS")
    print("VISA PIPELINE ✓" if passed == len(exports) else "VISA PIPELINE ✗")


if __name__ == "__main__":
    main()
