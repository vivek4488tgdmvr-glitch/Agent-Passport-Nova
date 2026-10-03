from pathlib import Path
import json

from agent_passport.opengap import run_checkpoints

ROOT = Path(__file__).resolve().parents[2]


def test_three_checkpoints_pass_for_repository():
    report = run_checkpoints(ROOT)
    assert report.status == "PASS"
    assert report.passed_count == 3
    assert report.total == 3
    assert [item.name for item in report.checkpoints] == [
        "VALIDATE", "EXPLAIN", "PASSPORT EVIDENCE"
    ]


def test_missing_explainability_fails_only_explain(tmp_path):
    for name in ("agent.yaml", "passport.yaml", "passport-travel-evidence-signed.json", "security-audit-report.json"):
        source = ROOT / name
        if source.exists():
            (tmp_path / name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "EXPLAINABILITY.md").write_text("too short", encoding="utf-8")
    report = run_checkpoints(tmp_path)
    assert report.status == "FAIL"
    assert report.checkpoints[0].status == "PASS"
    assert report.checkpoints[1].status == "FAIL"
    assert report.checkpoints[2].status == "PASS"


def test_report_is_serializable():
    report = run_checkpoints(ROOT)
    payload = json.loads(report.to_json())
    assert payload["total"] == 3
    assert payload["passed"] == 3
    assert payload["status"] == "PASS"


def test_checkpoint_three_rejects_tampered_evidence(tmp_path):
    import json, shutil
    from pathlib import Path
    from agent_passport.opengap.checkpoints import run_checkpoints

    root = Path(__file__).resolve().parents[2]
    for name in ("agent.yaml", "passport.yaml", "EXPLAINABILITY.md",
                 "passport-travel-evidence-signed.json", "security-audit-report.json"):
        shutil.copy(root / name, tmp_path / name)
    assert run_checkpoints(tmp_path).status == "PASS"

    p = tmp_path / "passport-travel-evidence-signed.json"
    data = json.loads(p.read_text())
    data["steps"][0]["detail"] = "TAMPERED"
    p.write_text(json.dumps(data))
    report = run_checkpoints(tmp_path)
    assert report.status == "FAIL"
    assert report.checkpoints[2].status == "FAIL"
