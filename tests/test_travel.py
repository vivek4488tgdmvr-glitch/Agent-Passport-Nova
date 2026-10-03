from agent_passport.travel import run_travel_demo


def test_complete_passport_travel():
    evidence = run_travel_demo()
    assert evidence.status == "PASS"
    assert evidence.failed == 0
    assert evidence.passed == 10
    assert evidence.steps[-1]["step"] == "PASSPORT TRAVEL"


def test_travel_contains_required_stages():
    evidence = run_travel_demo()
    names = [item["step"] for item in evidence.steps]
    required = {
        "AGENT IDENTITY",
        "PASSPORT TRUST",
        "CAPABILITY NEGOTIATION",
        "PORTABLE TOOL CONTRACT",
        "SECURITY POLICY",
        "BEHAVIORAL CONFORMANCE",
        "MULTI-AGENT DELEGATION",
        "RUNTIME MIGRATION",
        "POST-MIGRATION VERIFICATION",
        "PASSPORT TRAVEL",
    }
    assert required.issubset(names)
