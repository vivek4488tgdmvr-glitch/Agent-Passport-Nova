"""Encrypted-at-rest Ed25519 key storage.

Private signing material is never written to disk in plaintext by this module.
The keystore uses PBKDF2-HMAC-SHA256 to derive an encryption key from a
password and AES-256-GCM for authenticated encryption.  The password is
provided by the caller and is never persisted by the store.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import tempfile
from pathlib import Path
from typing import Any

from ..passport.signing import generate_keypair

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:  # pragma: no cover
    CRYPTOGRAPHY_AVAILABLE = False


FORMAT_VERSION = 1
KDF = "PBKDF2-HMAC-SHA256"
CIPHER = "AES-256-GCM"
DEFAULT_ITERATIONS = 600_000


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _unb64(value: str) -> bytes:
    return base64.b64decode(value.encode("ascii"), validate=True)


def _derive(password: str, salt: bytes, iterations: int) -> bytes:
    if not isinstance(password, str) or not password:
        raise ValueError("keystore password must be a non-empty string")
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations, dklen=32)


def _require_crypto() -> None:
    if not CRYPTOGRAPHY_AVAILABLE:
        raise RuntimeError("Secure key storage requires: pip install cryptography")


class SecureKeyStore:
    """Password-protected local keystore for one Ed25519 private key."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    @staticmethod
    def create(path: str | Path, password: str, *, issuer: str = "") -> dict[str, Any]:
        _require_crypto()
        private_key, public_key = generate_keypair()
        store = SecureKeyStore(path)
        store._write(private_key, public_key, password, issuer=issuer)
        return {"status": "PASS", "path": str(store.path), "public_key": public_key, "issuer": issuer}

    def _write(self, private_key: str, public_key: str, password: str, *, issuer: str) -> None:
        _require_crypto()
        salt = secrets.token_bytes(16)
        nonce = secrets.token_bytes(12)
        iterations = DEFAULT_ITERATIONS
        key = _derive(password, salt, iterations)
        plaintext = json.dumps({"private_key": private_key}, sort_keys=True, separators=(",", ":")).encode()
        aad = f"agent-passport-keystore:v{FORMAT_VERSION}".encode()
        ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
        payload = {
            "format_version": FORMAT_VERSION,
            "algorithm": CIPHER,
            "kdf": KDF,
            "iterations": iterations,
            "salt": _b64(salt),
            "nonce": _b64(nonce),
            "ciphertext": _b64(ciphertext),
            "public_key": public_key,
            "issuer": issuer,
        }
        self._atomic_write(payload)

    def _atomic_write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=f".{self.path.name}.", dir=str(self.path.parent), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.chmod(tmp, 0o600)
            except OSError:
                pass
            os.replace(tmp, self.path)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def metadata(self) -> dict[str, Any]:
        data = self._load_file()
        return {k: data[k] for k in ("format_version", "algorithm", "kdf", "iterations", "public_key", "issuer")}

    def public_key(self) -> str:
        return str(self._load_file()["public_key"])

    def load_private_key(self, password: str) -> str:
        _require_crypto()
        data = self._load_file()
        if data.get("format_version") != FORMAT_VERSION or data.get("algorithm") != CIPHER or data.get("kdf") != KDF:
            raise ValueError("unsupported or invalid keystore format")
        try:
            key = _derive(password, _unb64(data["salt"]), int(data["iterations"]))
            aad = f"agent-passport-keystore:v{FORMAT_VERSION}".encode()
            plaintext = AESGCM(key).decrypt(_unb64(data["nonce"]), _unb64(data["ciphertext"]), aad)
            private_key = json.loads(plaintext.decode())["private_key"]
        except Exception as exc:
            raise ValueError("keystore authentication failed") from exc
        return private_key

    def rotate(self, password: str, *, new_password: str | None = None, issuer: str | None = None) -> dict[str, Any]:
        # Authenticate access to the old key before replacing the encrypted file.
        self.load_private_key(password)
        new_private, new_public = generate_keypair()
        self._write(new_private, new_public, new_password or password, issuer=issuer if issuer is not None else self.metadata().get("issuer", ""))
        return {"status": "PASS", "public_key": new_public, "path": str(self.path)}

    def _load_file(self) -> dict[str, Any]:
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        with self.path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("invalid keystore")
        return data
