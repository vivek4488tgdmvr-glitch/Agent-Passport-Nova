"""Small smoke entry point for the Day 36 developer experience."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    required = ["agent.yaml", "README.md", "EXPLAINABILITY.md", "pyproject.toml"]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        raise SystemExit("Missing required repository files: " + ", ".join(missing))

    print("AGENT PASSPORT QUICKSTART")
    print("-------------------------")
    print("Repository structure: PASS")
    print("Root agent.yaml: PASS")
    print("Developer documentation: PASS")
    print("Ready for test suite: PASS")

if __name__ == "__main__":
    main()
