"""env_signature.py — sign and verify environment variable values."""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _signature_path(store_path: Path) -> Path:
    return store_path.parent / "signatures.json"


def _load_signatures(store_path: Path) -> dict:
    p = _signature_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_signatures(store_path: Path, data: dict) -> None:
    _signature_path(store_path).write_text(json.dumps(data, indent=2))


def _sign(value: str, secret: str) -> str:
    return hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()


@dataclass
class SignatureResult:
    key: str
    digest: str
    signed_at: float
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        status = "ok" if self.ok else f"error={self.error}"
        return f"<SignatureResult key={self.key!r} digest={self.digest[:12]}... {status}>"


def sign_variable(store_path: Path, key: str, value: str, secret: str) -> SignatureResult:
    """Sign *value* for *key* and persist the digest."""
    if not key:
        return SignatureResult(key=key, digest="", signed_at=0.0, ok=False, error="empty key")
    digest = _sign(value, secret)
    data = _load_signatures(store_path)
    data[key] = {"digest": digest, "signed_at": time.time()}
    _save_signatures(store_path, data)
    return SignatureResult(key=key, digest=digest, signed_at=data[key]["signed_at"], ok=True)


def verify_variable(store_path: Path, key: str, value: str, secret: str) -> SignatureResult:
    """Verify *value* against the stored digest for *key*."""
    data = _load_signatures(store_path)
    if key not in data:
        return SignatureResult(key=key, digest="", signed_at=0.0, ok=False, error="no signature")
    record = data[key]
    expected = _sign(value, secret)
    match = hmac.compare_digest(expected, record["digest"])
    return SignatureResult(
        key=key,
        digest=record["digest"],
        signed_at=record["signed_at"],
        ok=match,
        error=None if match else "digest mismatch",
    )


def remove_signature(store_path: Path, key: str) -> bool:
    data = _load_signatures(store_path)
    if key not in data:
        return False
    del data[key]
    _save_signatures(store_path, data)
    return True


def list_signatures(store_path: Path) -> list[dict]:
    data = _load_signatures(store_path)
    return [{"key": k, **v} for k, v in data.items()]
