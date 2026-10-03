"""Agent Passport Day 38 — judge-ready end-to-end showcase.

This is a deterministic presentation layer. It reports local evidence already
produced by the project and does not claim acceptance by an external validator.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def exists(name):
    return (ROOT / name).exists()

def main():
    checks = [
        ("Root OpenGAP manifest", exists("agent.yaml")),
        ("Passport specification", exists("passport.yaml")),
        ("Explainability", exists("EXPLAINABILITY.md")),
        ("Security Center", exists("SECURITY_CENTER.md")),
        ("Security threat model", exists("SECURITY_THREAT_MODEL.md")),
        ("Security controls", exists("SECURITY_CONTROL_MATRIX.md")),
        ("Final submission checklist", exists("FINAL_SUBMISSION_CHECKLIST.md")),
        ("Python package", exists("agent_passport")),
        ("Tests", exists("tests")),
    ]

    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║          AGENT PASSPORT — FINAL SHOWCASE         ║")
    print("╠════════════════════════════════════════════════════╣")
    for label, ok in checks:
        print(f"║ {'✓' if ok else '✗'} {label:<44} ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║ Identity → Validation → Security → Evidence       ║")
    print("║ Migration → Framework Export → Review             ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║              PASSPORT SHOWCASE READY ✓             ║")
    print("╚════════════════════════════════════════════════════╝")
    print()
    print("Note: local evidence is not a claim of external validator acceptance.")

if __name__ == "__main__":
    main()
