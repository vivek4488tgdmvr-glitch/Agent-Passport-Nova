from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_passport.opengap import export_opengap_agent, validate_agent_yaml


def main() -> None:
    print("=== DAY 31: OPENGAP COMPATIBILITY ===")
    agent_path = ROOT / "agent.yaml"
    doc = validate_agent_yaml(agent_path)
    print(f"Spec: {doc.spec}")
    print(f"Agent: {doc.agent['name']} v{doc.agent['version']}")
    print(f"Capabilities: {', '.join(doc.capabilities)}")
    print(f"Framework targets: {', '.join(doc.frameworks.targets)}")
    print("Root agent.yaml: PASS ✓")

    with tempfile.TemporaryDirectory() as temp_dir:
        generated = Path(temp_dir) / "agent.yaml"
        export_opengap_agent(ROOT / "passport.yaml", generated)
        validate_agent_yaml(generated)
    print("Passport → agent.yaml mapping: PASS ✓")
    print("OPEN GAP COMPATIBILITY: PASS ✓")


if __name__ == "__main__":
    main()
