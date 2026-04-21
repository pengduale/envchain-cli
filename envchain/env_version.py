"""Version tracking for individual environment variables."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional


def _version_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_versions.json"


def _load_versions(store_path: Path) -> dict:
    p = _version_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_versions(store_path: Path, data: dict) -> None:
    _version_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class VersionEntry:
    version: int
    timestamp: float
    preview: str

    def __repr__(self) -> str:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        return f"VersionEntry(v={self.version}, ts={ts!r}, preview={self.preview!r})"


def record_version(store_path: Path, key: str, value: str) -> VersionEntry:
    """Record a new version for a key's value."""
    data = _load_versions(store_path)
    entries = data.get(key, [])
    version_num = len(entries) + 1
    preview = value[:4] + "****" if len(value) > 4 else "****"
    entry = {"version": version_num, "timestamp": time.time(), "preview": preview}
    entries.append(entry)
    data[key] = entries
    _save_versions(store_path, data)
    return VersionEntry(**entry)


def get_versions(store_path: Path, key: str) -> List[VersionEntry]:
    """Return all recorded versions for a key."""
    data = _load_versions(store_path)
    return [VersionEntry(**e) for e in data.get(key, [])]


def get_latest_version(store_path: Path, key: str) -> Optional[VersionEntry]:
    """Return the most recent version entry for a key, or None."""
    versions = get_versions(store_path, key)
    return versions[-1] if versions else None


def clear_versions(store_path: Path, key: str) -> int:
    """Remove all version history for a key. Returns number of entries removed."""
    data = _load_versions(store_path)
    removed = len(data.pop(key, []))
    _save_versions(store_path, data)
    return removed


def list_versioned_keys(store_path: Path) -> List[str]:
    """Return all keys that have at least one version recorded."""
    data = _load_versions(store_path)
    return [k for k, v in data.items() if v]
