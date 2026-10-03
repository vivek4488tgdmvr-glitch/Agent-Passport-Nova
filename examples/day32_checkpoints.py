from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agent_passport.opengap import run_checkpoints


def main() -> None:
    print("=== DAY 32: OPENGAP THREE CHECKPOINTS ===")
    report = run_checkpoints(ROOT)
    print(report.pretty())
    output = ROOT / "opengap-checkpoint-report.json"
    output.write_text(report.to_json() + "\n", encoding="utf-8")
    print(f"Evidence: {output.name}")
    print("THREE CHECKPOINTS: PASS ✓" if report.status == "PASS" else "THREE CHECKPOINTS: FAIL ✗")
    raise SystemExit(0 if report.status == "PASS" else 1)


if __name__ == "__main__":
    main()
