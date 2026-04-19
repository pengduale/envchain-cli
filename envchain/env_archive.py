"""Archive (soft-delete) and restore variables within a store."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _archive_path(store_path: Path) -> Path:
    return store_path.parent / (store_path.stem + ".archive.json")


def _load_archive(store_path: Path) -> dict:
    p = _archive_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_archive(store_path: Path, data: dict) -> None:
    _archive_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ArchiveResult:
    key: str
    action: str  # 'archived' | 'restored' | 'purged'
    ok: bool
    reason: Optional[str] = None

    def __repr__(self) -> str:
        return f"<ArchiveResult {self.action} {self.key!r} ok={self.ok}>"


def archive_variable(store_path: Path, key: str, encrypted_value: str) -> ArchiveResult:
    """Move an encrypted value to the archive store."""
    data = _load_archive(store_path)
    data[key] = encrypted_value
    _save_archive(store_path, data)
    return ArchiveResult(key=key, action="archived", ok=True)


def restore_variable(store_path: Path, key: str) -> ArchiveResult:
    """Return archived encrypted value and remove it from archive."""
    data = _load_archive(store_path)
    if key not in data:
        return ArchiveResult(key=key, action="restored", ok=False, reason="not in archive")
    value = data.pop(key)
    _save_archive(store_path, data)
    return ArchiveResult(key=key, action="restored", ok=True, reason=value)


def list_archived(store_path: Path) -> list[str]:
    return list(_load_archive(store_path).keys())


def purge_variable(store_path: Path, key: str) -> ArchiveResult:
    data = _load_archive(store_path)
    if key not in data:
        return ArchiveResult(key=key, action="purged", ok=False, reason="not in archive")
    data.pop(key)
    _save_archive(store_path, data)
    return ArchiveResult(key=key, action="purged", ok=True)
