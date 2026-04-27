"""Trust level management for environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("untrusted", "low", "medium", "high", "verified")


def _trust_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_trust.json"


def _load_trust(store_path: Path) -> dict:
    p = _trust_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_trust(store_path: Path, data: dict) -> None:
    _trust_path(store_path).write_text(json.dumps(data, indent=2))


class TrustResult:
    def __init__(self, key: str, level: str, ok: bool, message: str = ""):
        self.key = key
        self.level = level
        self.ok = ok
        self.message = message

    def __repr__(self) -> str:
        return f"TrustResult(key={self.key!r}, level={self.level!r}, ok={self.ok})"


def set_trust(store_path: Path, key: str, level: str) -> TrustResult:
    """Assign a trust level to a key."""
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid trust level {level!r}. Must be one of: {VALID_LEVELS}")
    data = _load_trust(store_path)
    data[key] = level
    _save_trust(store_path, data)
    return TrustResult(key=key, level=level, ok=True, message=f"Trust level set to '{level}'")


def get_trust(store_path: Path, key: str) -> Optional[str]:
    """Return the trust level for a key, or None if unset."""
    return _load_trust(store_path).get(key)


def remove_trust(store_path: Path, key: str) -> bool:
    """Remove the trust level entry for a key. Returns True if it existed."""
    data = _load_trust(store_path)
    if key not in data:
        return False
    del data[key]
    _save_trust(store_path, data)
    return True


def list_trust(store_path: Path) -> dict:
    """Return all key -> trust-level mappings."""
    return dict(_load_trust(store_path))
