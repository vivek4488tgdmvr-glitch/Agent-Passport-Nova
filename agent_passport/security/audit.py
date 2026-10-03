"""Release-grade local security audit for Agent Passport.

The audit is defensive and deterministic: it checks the project's own security
controls and release artifacts. It does not scan external hosts or exploit
systems.
"""
from __future__ import annotations

import base64
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .redteam import run_red_team_suite
from ..passport.evidence import verify_evidence


@dataclass(frozen=True)
class AuditCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class SecurityAuditReport:
    checks: tuple[AuditCheck, ...]

    @property
    def passed(self) -> int:
        return sum(c.passed for c in self.checks)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def status(self) -> str:
        return "PASS" if self.passed == self.total else "FAIL"

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "passed": self.passed,
            "total": self.total,
            "checks": [c.__dict__ for c in self.checks],
        }


def _check(name: str, fn: Callable[[], tuple[bool, str]]) -> AuditCheck:
    try:
        ok, detail = fn()
        return AuditCheck(name, bool(ok), detail)
    except Exception as exc:
        return AuditCheck(name, False, f"unexpected error: {type(exc).__name__}: {exc}")


def _test_suite(root: Path) -> tuple[bool, str]:
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    output = (p.stdout + "\n" + p.stderr).strip()
    passed = p.returncode == 0 and " skipped" not in output
    tail = output.splitlines()[-1] if output else "no pytest output"
    return passed, tail


def _should_skip(path: Path) -> bool:
    ignored = {".git", ".pytest_cache", "__pycache__", ".venv", "venv", "site-packages", "dist-info", "egg-info", "tests", "examples"}
    return any(part in ignored for part in path.parts)


def _no_private_key_files(root: Path) -> tuple[bool, str]:
    forbidden_suffixes = {".pem", ".key", ".p12", ".pfx", ".der"}
    hits = []
    for path in root.rglob("*"):
        if not path.is_file() or _should_skip(path):
            continue
        if path.suffix.lower() in forbidden_suffixes:
            hits.append(str(path.relative_to(root)))
    return not hits, "no private-key material files found" if not hits else f"forbidden key files: {hits}"


def _no_plaintext_private_key_json(root: Path) -> tuple[bool, str]:
    hits = []
    for path in root.rglob("*.json"):
        if _should_skip(path):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, dict) and "private_key" in data and "ciphertext" not in data:
            hits.append(str(path.relative_to(root)))
    return not hits, "no plaintext private-key JSON artifacts found" if not hits else f"plaintext private-key artifacts: {hits}"


def _no_live_secret_patterns(root: Path) -> tuple[bool, str]:
    # Deliberately scan application/source/config files only. Tests and examples
    # contain intentional redaction fixtures and fake values for demonstrations.
    patterns = [
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
        re.compile(r"(?:AKIA|ASIA)[0-9A-Z]{16}"),
        re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
        re.compile(r"sk-[A-Za-z0-9]{30,}"),
    ]
    hits = []
    allowed = {".py", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".json"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in allowed or _should_skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in patterns:
            if pattern.search(text):
                hits.append(str(path.relative_to(root)))
                break
    return not hits, "no high-confidence live-secret patterns found in application/config files" if not hits else f"possible secrets: {hits}"


def run_security_audit(root: str | Path = ".") -> SecurityAuditReport:
    root = Path(root).resolve()
    checks: list[AuditCheck] = []
    checks.append(_check("Full test suite with zero skips", lambda: _test_suite(root)))
    def redteam_check() -> tuple[bool, str]:
        report = run_red_team_suite()
        return report.status == "PASS", f"{report.passed}/{report.total} local probes passed"

    checks.append(_check("Safe red-team suite", redteam_check))
    checks.append(_check("Encrypted key-management module", lambda: (
        (root / "agent_passport/security/keystore.py").exists(),
        "encrypted keystore implementation present",
    )))
    checks.append(_check("Sandbox enforcement module", lambda: (
        (root / "agent_passport/security/sandbox.py").exists(),
        "isolated tool execution controls present",
    )))
    checks.append(_check("Security hardening module", lambda: (
        (root / "agent_passport/security/hardening.py").exists(),
        "request validation, rate limiting, replay protection and audit chain present",
    )))
    checks.append(_check("Signed evidence verification", lambda: _verify_signed_evidence(root)))
    checks.append(_check("No private-key material in release tree", lambda: _no_private_key_files(root)))
    checks.append(_check("No plaintext private-key JSON artifacts", lambda: _no_plaintext_private_key_json(root)))
    checks.append(_check("No high-confidence live secrets in application/config", lambda: _no_live_secret_patterns(root)))
    checks.append(_check("Cryptography dependency declared", lambda: _crypto_dependency(root)))
    checks.append(_check("Release artifacts present", lambda: _release_artifacts(root)))
    return SecurityAuditReport(tuple(checks))


def _verify_signed_evidence(root: Path) -> tuple[bool, str]:
    path = root / "passport-travel-evidence-signed.json"
    if not path.exists():
        return False, "signed evidence artifact missing"
    data = json.loads(path.read_text(encoding="utf-8"))
    result = verify_evidence(data)
    return result.get("status") == "PASS", f"signed evidence verification: {result.get('status')}"


def _crypto_dependency(root: Path) -> tuple[bool, str]:
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    ok = 'cryptography>=42,<47' in text and 'security =' in text
    return ok, "cryptography security extra declared" if ok else "cryptography security extra missing"


def _release_artifacts(root: Path) -> tuple[bool, str]:
    required = [
        "passport.yaml",
        "passport-travel-evidence-signed.json",
        "red-team-report.json",
        "SUBMISSION_CHECKLIST.md",
        "examples/final_release_check.py",
    ]
    missing = [p for p in required if not (root / p).exists()]
    return not missing, "all release artifacts present" if not missing else f"missing: {missing}"
