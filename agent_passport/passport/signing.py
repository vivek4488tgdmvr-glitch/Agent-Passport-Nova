"""Passport signing and verification using Ed25519 when available.

The Passport fingerprint remains a deterministic content identifier.
Signatures add authenticity/integrity; they do not replace the fingerprint.
"""

from __future__ import annotations

import base64
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives import serialization
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


def _canonical(data: dict[str, Any]) -> bytes:
    return json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _payload(passport: dict[str, Any]) -> dict[str, Any]:
    # Signature metadata itself is excluded from the signed payload.
    data = json.loads(json.dumps(passport))
    data.pop("signature", None)
    return data


def generate_keypair() -> tuple[str, str]:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError(
            "Ed25519 signing requires: pip install cryptography"
        )
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    private_raw = private.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )
    public_raw = public.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return (
        base64.b64encode(private_raw).decode(),
        base64.b64encode(public_raw).decode(),
    )


def sign_passport(passport: dict[str, Any], private_key_b64: str, issuer: str) -> dict[str, Any]:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError(
            "Ed25519 signing requires: pip install cryptography"
        )
    private_raw = base64.b64decode(private_key_b64)
    private = Ed25519PrivateKey.from_private_bytes(private_raw)
    payload = _canonical(_payload(passport))
    signature = private.sign(payload)
    digest = hashlib.sha256(payload).hexdigest()
    result = dict(passport)
    result["signature"] = {
        "algorithm": "Ed25519",
        "issuer": issuer,
        "signed_at": datetime.now(timezone.utc).isoformat(),
        "content_sha256": digest,
        "signature": base64.b64encode(signature).decode(),
    }
    return result


def verify_signature(passport: dict[str, Any], public_key_b64: str) -> dict[str, Any]:
    if not CRYPTOGRAPHY_AVAILABLE:
        return {
            "status": "SKIP",
            "reason": "cryptography package is not installed",
        }

    signature = passport.get("signature")
    if not signature:
        return {"status": "FAIL", "reason": "Passport has no signature"}

    if signature.get("algorithm") != "Ed25519":
        return {
            "status": "FAIL",
            "reason": f"Unsupported algorithm: {signature.get('algorithm')}",
        }

    payload = _canonical(_payload(passport))
    digest = hashlib.sha256(payload).hexdigest()
    if digest != signature.get("content_sha256"):
        return {
            "status": "FAIL",
            "reason": "Signed content hash does not match Passport contents",
        }

    try:
        public = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(public_key_b64)
        )
        public.verify(
            base64.b64decode(signature["signature"]),
            payload,
        )
    except Exception:
        return {"status": "FAIL", "reason": "Ed25519 signature verification failed"}

    return {
        "status": "PASS",
        "issuer": signature.get("issuer"),
        "signed_at": signature.get("signed_at"),
        "content_sha256": digest,
    }
