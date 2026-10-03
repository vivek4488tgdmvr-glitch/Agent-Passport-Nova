"""Cryptographic signing and verification for Passport Travel evidence."""

from __future__ import annotations

import base64
import hashlib
import json
from typing import Any

from .fingerprint import fingerprint
from .loader import load
from .signing import Ed25519PrivateKey, Ed25519PublicKey, CRYPTOGRAPHY_AVAILABLE


def _canonical(data: dict[str, Any]) -> bytes:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _payload(evidence: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(evidence))
    data.pop("cryptographic_evidence", None)
    return data


def evidence_hash(evidence: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical(_payload(evidence))).hexdigest()


def sign_evidence(
    evidence: dict[str, Any],
    passport_fingerprint: str,
    private_key_b64: str,
    issuer: str,
) -> dict[str, Any]:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("Evidence signing requires: pip install cryptography")
    private = Ed25519PrivateKey.from_private_bytes(base64.b64decode(private_key_b64))
    payload = _canonical(_payload(evidence))
    digest = hashlib.sha256(payload).hexdigest()
    signature = private.sign(payload)
    from cryptography.hazmat.primitives import serialization
    public = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    result = json.loads(json.dumps(evidence))
    result["cryptographic_evidence"] = {
        "algorithm": "Ed25519",
        "issuer": issuer,
        "passport_fingerprint": passport_fingerprint,
        "evidence_sha256": digest,
        "public_key": base64.b64encode(public).decode("ascii"),
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    return result


def verify_evidence(
    evidence: dict[str, Any],
    expected_passport_fingerprint: str | None = None,
) -> dict[str, Any]:
    if not CRYPTOGRAPHY_AVAILABLE:
        return {"status": "SKIP", "reason": "cryptography package is not installed"}
    meta = evidence.get("cryptographic_evidence")
    if not isinstance(meta, dict):
        return {"status": "FAIL", "reason": "Evidence has no cryptographic envelope"}
    if meta.get("algorithm") != "Ed25519":
        return {"status": "FAIL", "reason": "Unsupported evidence signature algorithm"}
    passport_fp = meta.get("passport_fingerprint")
    if not passport_fp:
        return {"status": "FAIL", "reason": "Evidence has no Passport fingerprint"}
    if expected_passport_fingerprint is not None and passport_fp != expected_passport_fingerprint:
        return {"status": "FAIL", "reason": "Evidence is bound to a different Passport fingerprint"}

    payload = _canonical(_payload(evidence))
    digest = hashlib.sha256(payload).hexdigest()
    if digest != meta.get("evidence_sha256"):
        return {"status": "FAIL", "reason": "Evidence hash does not match evidence contents"}
    try:
        public = Ed25519PublicKey.from_public_bytes(base64.b64decode(meta["public_key"]))
        public.verify(base64.b64decode(meta["signature"]), payload)
    except Exception:
        return {"status": "FAIL", "reason": "Ed25519 evidence signature verification failed"}
    return {
        "status": "PASS",
        "issuer": meta.get("issuer"),
        "passport_fingerprint": passport_fp,
        "evidence_sha256": digest,
    }


def passport_fingerprint_from_file(path: str) -> str:
    return fingerprint(load(path))
