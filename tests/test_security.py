import pytest

from agent_passport.security import PermissionPolicy, SecurityEngine, PermissionDecision
from agent_passport.tools import PortableTool, SecureToolRegistry
from agent_passport.verification.security_checks import verify_policy


def test_allowed_permission():
    engine = SecurityEngine(PermissionPolicy(
        allow=frozenset({"network"})
    ))
    result = engine.check({"network"})
    assert result.allowed
    assert result.decision == PermissionDecision.ALLOW


def test_missing_permission_denied():
    engine = SecurityEngine(PermissionPolicy(
        allow=frozenset({"network"})
    ))
    result = engine.check({"filesystem_read"})
    assert not result.allowed
    assert result.missing == ("filesystem_read",)


def test_explicit_deny_wins():
    engine = SecurityEngine(PermissionPolicy(
        allow=frozenset({"network"}),
        deny=frozenset({"network"})
    ))
    result = engine.check({"network"})
    assert result.decision == PermissionDecision.DENY
    assert result.denied == ("network",)


def test_require_raises_on_denial():
    engine = SecurityEngine(PermissionPolicy())
    with pytest.raises(PermissionError):
        engine.require({"shell"})


def test_policy_verification_rejects_overlap():
    result = verify_policy(PermissionPolicy(
        allow=frozenset({"network"}),
        deny=frozenset({"network"})
    ))
    assert result["status"] == "FAIL"


def test_secure_registry_allows_permitted_tool():
    tool = PortableTool(
        "calculator", "1.0.0", "adds numbers", {}, "number",
        permissions={"network": False}
    )
    registry = SecureToolRegistry(PermissionPolicy())
    registry.register(tool)
    registry.bind("calculator", "native", lambda a, b: a + b)
    assert registry.invoke("calculator", "native", 2, 3) == 5


def test_secure_registry_blocks_network_tool():
    tool = PortableTool(
        "web_search", "1.0.0", "searches web", {}, "object",
        permissions={"network": True}
    )
    registry = SecureToolRegistry(PermissionPolicy())
    registry.register(tool)
    registry.bind("web_search", "native", lambda q: {"q": q})
    with pytest.raises(PermissionError):
        registry.invoke("web_search", "native", "hello")


def test_secure_registry_allows_network_when_policy_grants_it():
    tool = PortableTool(
        "web_search", "1.0.0", "searches web", {}, "object",
        permissions={"network": True}
    )
    registry = SecureToolRegistry(
        PermissionPolicy(allow=frozenset({"network"}))
    )
    registry.register(tool)
    registry.bind("web_search", "native", lambda q: {"q": q})
    assert registry.invoke("web_search", "native", "hello") == {"q": "hello"}
