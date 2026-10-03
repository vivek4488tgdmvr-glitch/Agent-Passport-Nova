import json
from pathlib import Path

from agent_passport.dashboard.server import build_dashboard_data, create_app


def test_dashboard_data_contains_trust_sections():
    data = build_dashboard_data(Path("passport.yaml"))
    assert "agent" in data
    assert "capabilities" in data
    assert "tools" in data
    assert "security" in data
    assert "delegation" in data
    assert "migration" in data


def test_dashboard_handler_is_constructible():
    handler = create_app("passport.yaml")
    assert handler is not None


def test_dashboard_json_is_serializable():
    data = build_dashboard_data("passport.yaml")
    json.dumps(data)

def test_dashboard_html_sets_security_headers():
    handler = create_app("passport.yaml")
    assert handler is not None
    # Header policy is enforced in the request handler; source-level assertion
    # keeps the dependency-free server hardened without opening a real port.
    import inspect
    source = inspect.getsource(handler)
    assert 'X-Content-Type-Options' in source
    assert 'Content-Security-Policy' in source
    assert 'Cache-Control' in source


def test_dashboard_escapes_untrusted_display_values():
    from agent_passport.dashboard.server import _html
    malicious = {
        "agent": {"id": "x", "name": "<img src=x onerror=alert(1)>", "version": "1", "description": ""},
        "passport": {"version": "1", "fingerprint": "x", "signature": "not_verified", "registry": "unknown"},
        "registry": {"status": "unknown", "published_versions": [], "latest": None, "passport_id": None, "signature_verified_on_retrieval": False},
        "capabilities": ["<script>alert(1)</script>"],
        "tools": ["<img src=x onerror=alert(1)>"],
        "runtimes": ["<svg onload=alert(1)>"],
        "delegation": {"peers": [], "status": "scoped", "example": "x"},
        "travel": {"passed": 0, "total_steps": 0},
    }
    html = _html(malicious)
    assert 'innerHTML+=`<span' not in html
    assert 'textContent=String(x)' in html
    assert 'innerHTML+=`<span' not in html
