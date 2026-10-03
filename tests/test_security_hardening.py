from agent_passport.security import (
    RequestGuard, SlidingWindowRateLimiter, ReplayGuard,
    redact_secrets, TamperEvidentAuditLog,
)


def test_request_guard_rejects_malformed_principal_and_oversized_body():
    guard = RequestGuard(max_body_bytes=4)
    assert not guard.validate("../../etc/passwd").allowed
    assert not guard.validate("nova", body=b"12345").allowed
    assert guard.validate("nova", request_id="req-1", body=b"1234").allowed


def test_rate_limiter_blocks_after_limit_and_recovers():
    now = [0.0]
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=10, clock=lambda: now[0])
    assert limiter.allow("nova")
    assert limiter.allow("nova")
    assert not limiter.allow("nova")
    assert limiter.remaining("nova") == 0
    now[0] = 11.0
    assert limiter.allow("nova")


def test_rate_limits_are_isolated_per_principal():
    limiter = SlidingWindowRateLimiter(max_requests=1, window_seconds=60, clock=lambda: 1.0)
    assert limiter.allow("nova")
    assert limiter.allow("scout")
    assert not limiter.allow("nova")


def test_replay_guard_accepts_nonce_once():
    guard = ReplayGuard(max_entries=2)
    assert guard.accept_once("n1")
    assert not guard.accept_once("n1")
    assert guard.accept_once("n2")
    assert guard.accept_once("n3")  # bounded cache evicts oldest
    assert not guard.accept_once("n3")


def test_secret_redaction_is_recursive():
    value = {"token": "secret", "nested": {"api_key": "abc", "safe": "ok"}, "items": [{"password": "pw"}]}
    safe = redact_secrets(value)
    assert safe["token"] == "[REDACTED]"
    assert safe["nested"]["api_key"] == "[REDACTED]"
    assert safe["items"][0]["password"] == "[REDACTED]"
    assert safe["nested"]["safe"] == "ok"
    assert value["token"] == "secret"


def test_audit_log_is_tamper_evident_and_redacts_credentials():
    audit = TamperEvidentAuditLog()
    audit.append("AUTHZ", principal="nova", result="DENY", details={"token": "do-not-log", "tool": "shell"})
    audit.append("AUTHZ", principal="nova", result="ALLOW", details={"tool": "calculator"})
    assert audit.verify()
    entries = audit.entries()
    assert entries[0]["details"]["token"] == "[REDACTED]"
    entries[0]["result"] = "ALLOW"
    audit._entries[0] = entries[0]  # simulate storage tampering
    assert not audit.verify()
