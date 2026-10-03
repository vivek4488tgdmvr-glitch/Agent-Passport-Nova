import pytest

from agent_passport.delegation import (
    AgentPeer,
    DelegationEngine,
    DelegationRequest,
    DelegationToken,
)


def peers():
    nova = AgentPeer(
        "nova", "Nova", "1.0.0",
        capabilities=frozenset({"reasoning", "web_search"}),
        tools=frozenset({"web_search"}),
        issuer="demo",
        passport_fingerprint="abc123",
    )
    scout = AgentPeer(
        "scout", "Scout", "1.0.0",
        capabilities=frozenset({"web_search", "summarization"}),
        tools=frozenset({"web_search"}),
    )
    return nova, scout


def test_matching_delegation_allowed():
    nova, scout = peers()
    engine = DelegationEngine([nova, scout])
    result = engine.evaluate(DelegationRequest(
        "nova", "scout",
        capabilities=frozenset({"summarization"}),
        tools=frozenset({"web_search"}),
        purpose="summarize search results",
    ))
    assert result.allowed


def test_missing_capability_denied():
    nova, scout = peers()
    engine = DelegationEngine([nova, scout])
    result = engine.evaluate(DelegationRequest(
        "nova", "scout",
        capabilities=frozenset({"code_execution"}),
    ))
    assert not result.allowed
    assert result.missing_capabilities == ("code_execution",)


def test_missing_tool_denied():
    nova, scout = peers()
    engine = DelegationEngine([nova, scout])
    result = engine.evaluate(DelegationRequest(
        "nova", "scout",
        tools=frozenset({"shell_exec"}),
    ))
    assert not result.allowed
    assert result.missing_tools == ("shell_exec",)


def test_unknown_target_denied():
    nova, _ = peers()
    engine = DelegationEngine([nova])
    result = engine.evaluate(DelegationRequest(
        "nova", "missing", capabilities=frozenset({"web_search"})
    ))
    assert not result.allowed


def test_unknown_requester_denied():
    _, scout = peers()
    engine = DelegationEngine([scout])
    result = engine.evaluate(DelegationRequest(
        "missing", "scout", capabilities=frozenset({"web_search"})
    ))
    assert not result.allowed


def test_self_delegation_denied():
    nova, _ = peers()
    engine = DelegationEngine([nova])
    result = engine.evaluate(DelegationRequest("nova", "nova"))
    assert not result.allowed


def test_invalid_use_count_denied():
    nova, scout = peers()
    engine = DelegationEngine([nova, scout])
    result = engine.evaluate(DelegationRequest("nova", "scout", max_uses=0))
    assert not result.allowed


def test_require_raises_on_denial():
    nova, scout = peers()
    engine = DelegationEngine([nova, scout])
    with pytest.raises(PermissionError):
        engine.require(DelegationRequest(
            "nova", "scout",
            capabilities=frozenset({"shell"}),
        ))


def test_delegation_token_is_scoped():
    token = DelegationToken(
        "nova", "scout",
        frozenset({"summarization"}),
        frozenset({"web_search"}),
        "summarize search results",
        1,
    )
    assert token.allows_capability("summarization")
    assert not token.allows_capability("shell")
    assert token.allows_tool("web_search")
    assert not token.allows_tool("shell_exec")


def test_peer_serialization():
    nova, _ = peers()
    data = nova.to_dict()
    assert data["agent_id"] == "nova"
    assert "web_search" in data["capabilities"]
