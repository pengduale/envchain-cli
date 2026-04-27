"""Read-only lock for individual environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


def _readonly_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_readonly.json"


def _load_readonly(store_path: Path) -> dict:
    p = _readonly_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_readonly(store_path: Path, data: dict) -> None:
    _readonly_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ReadonlyResult:
    key: str
    locked: bool
    ok: bool
    message: str

    def __repr__(self) -> str:
        status = "locked" if self.locked else "unlocked"
        return f"<ReadonlyResult key={self.key!r} status={status} ok={self.ok}>"


def set_readonly(store_path: Path, key: str, locked: bool = True) -> ReadonlyResult:
    """Mark a key as read-only (or remove the lock)."""
    data = _load_readonly(store_path)
    data[key] = locked
    _save_readonly(store_path, data)
    action = "locked" if locked else "unlocked"
    return ReadonlyResult(key=key, locked=locked, ok=True, message=f"{key} marked as {action}")


def is_readonly(store_path: Path, key: str) -> bool:
    """Return True if the key is marked read-only."""
    data = _load_readonly(store_path)
    return bool(data.get(key, False))


def remove_readonly(store_path: Path, key: str) -> ReadonlyResult:
    """Remove the read-only flag from a key."""
    data = _load_readonly(store_path)
    if key not in data:
        return ReadonlyResult(key=key, locked=False, ok=False, message=f"{key} has no readonly entry")
    del data[key]
    _save_readonly(store_path, data)
    return ReadonlyResult(key=key, locked=False, ok=True, message=f"{key} readonly entry removed")


def list_readonly_keys(store_path: Path) -> list[str]:
    """Return all keys that are currently marked read-only."""
    data = _load_readonly(store_path)
    return [k for k, v in data.items() if v]
