from agent_passport.security.redteam import run_red_team_suite


def test_safe_red_team_suite_passes_all_probes():
    report = run_red_team_suite()
    assert report.status == "PASS"
    assert report.passed == report.total
    assert report.total >= 11


def test_red_team_report_is_serializable():
    report = run_red_team_suite().to_dict()
    assert report["status"] == "PASS"
    assert all("name" in probe and "passed" in probe for probe in report["probes"])
