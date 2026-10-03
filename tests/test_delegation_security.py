from datetime import datetime, timedelta, timezone

from agent_passport.delegation import AgentPeer, DelegationEngine, DelegationRequest


def setup_engine():
    nova = AgentPeer("nova", "Nova", "1.0.0", frozenset({"reasoning"}), frozenset())
    scout = AgentPeer("scout", "Scout", "1.0.0", frozenset({"web_search", "summarization"}), frozenset({"web_search"}))
    return DelegationEngine([nova, scout])


def test_token_expires_and_is_rejected():
    engine = setup_engine()
    token = engine.issue(DelegationRequest("nova", "scout", frozenset({"web_search"})), ttl_seconds=1)
    future = datetime.now(timezone.utc) + timedelta(seconds=2)
    result = engine.consume(token, DelegationRequest("nova", "scout", frozenset({"web_search"})), now=future)
    assert not result.allowed
    assert "expired" in result.reason


def test_replay_is_rejected_after_max_use():
    engine = setup_engine()
    req = DelegationRequest("nova", "scout", frozenset({"web_search"}), max_uses=1)
    token = engine.issue(req)
    assert engine.consume(token, req).allowed
    replay = engine.consume(token, req)
    assert not replay.allowed
    assert "replay" in replay.reason


def test_max_uses_allows_exact_number_of_consumptions():
    engine = setup_engine()
    req = DelegationRequest("nova", "scout", frozenset({"web_search"}), max_uses=2)
    token = engine.issue(req)
    assert engine.consume(token, req).allowed
    assert engine.consume(token, req).allowed
    assert not engine.consume(token, req).allowed
    assert engine.usage_count(token) == 2


def test_permission_escalation_is_denied():
    engine = setup_engine()
    token = engine.issue(DelegationRequest("nova", "scout", frozenset({"web_search"})))
    escalated = DelegationRequest("nova", "scout", frozenset({"web_search", "summarization"}))
    result = engine.consume(token, escalated)
    assert not result.allowed
    assert "escalation" in result.reason


def test_audit_log_records_security_events():
    engine = setup_engine()
    req = DelegationRequest("nova", "scout", frozenset({"web_search"}))
    token = engine.issue(req)
    engine.consume(token, req)
    engine.consume(token, req)
    events = engine.audit_log()
    assert [e["event"] for e in events] == ["ISSUED", "CONSUMED", "DENIED"]
    assert all(e["token_id"] == token.token_id for e in events)
