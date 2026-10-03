from pathlib import Path
from unittest.mock import patch

from agent_passport.security.audit import run_security_audit


ROOT = Path(__file__).resolve().parents[1]


def test_security_audit_structure():
    # The standalone audit runs pytest itself; patch that nested invocation here
    # so the unit test cannot recursively invoke the test suite.
    with patch("agent_passport.security.audit._test_suite", return_value=(True, "123 passed, 0 skipped")):
        report = run_security_audit(ROOT)
    assert report.status == "PASS", report.to_dict()
    assert report.passed == report.total


def test_security_audit_is_serializable():
    with patch("agent_passport.security.audit._test_suite", return_value=(True, "123 passed, 0 skipped")):
        report = run_security_audit(ROOT)
    data = report.to_dict()
    assert data["status"] == "PASS"
    assert len(data["checks"]) >= 10


def test_security_audit_rejects_plaintext_private_key_json(tmp_path):
    from agent_passport.security.audit import _no_plaintext_private_key_json
    (tmp_path / "keys.json").write_text('{"private_key":"SECRET"}', encoding="utf-8")
    ok, detail = _no_plaintext_private_key_json(tmp_path)
    assert not ok
    assert "plaintext" in detail
