"""Track a human-readable changelog entry per environment variable."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


def _changelog_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_changelog.json"


def _load_changelog(store_path: Path) -> dict:
    p = _changelog_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_changelog(store_path: Path, data: dict) -> None:
    _changelog_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ChangelogEntry:
    key: str
    message: str
    author: Optional[str]
    timestamp: str

    def __repr__(self) -> str:
        author_part = f" ({self.author})" if self.author else ""
        return f"[{self.timestamp}]{author_part} {self.key}: {self.message}"


def add_changelog_entry(
    store_path: Path,
    key: str,
    message: str,
    author: Optional[str] = None,
) -> ChangelogEntry:
    if not key.strip():
        raise ValueError("key must not be empty")
    if not message.strip():
        raise ValueError("message must not be empty")

    data = _load_changelog(store_path)
    entries = data.get(key, [])
    ts = datetime.now(timezone.utc).isoformat()
    entry = ChangelogEntry(key=key, message=message, author=author, timestamp=ts)
    entries.append(asdict(entry))
    data[key] = entries
    _save_changelog(store_path, data)
    return entry


def get_changelog_entries(store_path: Path, key: str) -> List[ChangelogEntry]:
    data = _load_changelog(store_path)
    return [ChangelogEntry(**e) for e in data.get(key, [])]


def clear_changelog(store_path: Path, key: str) -> bool:
    data = _load_changelog(store_path)
    if key not in data:
        return False
    del data[key]
    _save_changelog(store_path, data)
    return True


def list_keys_with_changelog(store_path: Path) -> List[str]:
    return list(_load_changelog(store_path).keys())
