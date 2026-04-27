"""Retention policy management for envchain variables.

Allows setting a retention duration (in days) for keys, after which
they are considered eligible for cleanup or archival.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


def _retention_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_retention.json"


def _load_retention(store_path: Path) -> dict:
    p = _retention_path(store_path)
    if not p.exists():
        return {}
    with p.open("r") as f:
        return json.load(f)


def _save_retention(store_path: Path, data: dict) -> None:
    p = _retention_path(store_path)
    with p.open("w") as f:
        json.dump(data, f, indent=2)


@dataclass
class RetentionResult:
    key: str
    retain_days: int
    set_at: str
    expires_at: str
    ok: bool
    message: str

    def __repr__(self) -> str:
        return (
            f"RetentionResult(key={self.key!r}, retain_days={self.retain_days}, "
            f"expires_at={self.expires_at!r}, ok={self.ok})"
        )


def set_retention(store_path: Path, key: str, retain_days: int) -> RetentionResult:
    """Set a retention policy for a key (how many days to keep it)."""
    if retain_days <= 0:
        raise ValueError("retain_days must be a positive integer")

    data = _load_retention(store_path)
    now = datetime.utcnow()
    expires = now + timedelta(days=retain_days)

    data[key] = {
        "retain_days": retain_days,
        "set_at": now.isoformat(),
        "expires_at": expires.isoformat(),
    }
    _save_retention(store_path, data)

    return RetentionResult(
        key=key,
        retain_days=retain_days,
        set_at=now.isoformat(),
        expires_at=expires.isoformat(),
        ok=True,
        message=f"Retention set: {retain_days} days (expires {expires.date()})",
    )


def get_retention(store_path: Path, key: str) -> Optional[RetentionResult]:
    """Retrieve the retention policy for a key, or None if not set."""
    data = _load_retention(store_path)
    entry = data.get(key)
    if entry is None:
        return None
    return RetentionResult(
        key=key,
        retain_days=entry["retain_days"],
        set_at=entry["set_at"],
        expires_at=entry["expires_at"],
        ok=True,
        message="",
    )


def remove_retention(store_path: Path, key: str) -> bool:
    """Remove the retention policy for a key. Returns True if it existed."""
    data = _load_retention(store_path)
    if key not in data:
        return False
    del data[key]
    _save_retention(store_path, data)
    return True


def is_expired(store_path: Path, key: str) -> bool:
    """Return True if the key's retention period has elapsed."""
    result = get_retention(store_path, key)
    if result is None:
        return False
    expires = datetime.fromisoformat(result.expires_at)
    return datetime.utcnow() > expires


def list_expired(store_path: Path) -> List[RetentionResult]:
    """Return all keys whose retention period has elapsed."""
    data = _load_retention(store_path)
    now = datetime.utcnow()
    expired = []
    for key, entry in data.items():
        expires = datetime.fromisoformat(entry["expires_at"])
        if now > expires:
            expired.append(
                RetentionResult(
                    key=key,
                    retain_days=entry["retain_days"],
                    set_at=entry["set_at"],
                    expires_at=entry["expires_at"],
                    ok=True,
                    message="expired",
                )
            )
    return expired


def list_retention(store_path: Path) -> List[RetentionResult]:
    """Return all keys that have a retention policy set."""
    data = _load_retention(store_path)
    results = []
    for key, entry in data.items():
        results.append(
            RetentionResult(
                key=key,
                retain_days=entry["retain_days"],
                set_at=entry["set_at"],
                expires_at=entry["expires_at"],
                ok=True,
                message="",
            )
        )
    return results
