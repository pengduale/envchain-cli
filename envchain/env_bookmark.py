"""Bookmark support: save named references to key+profile pairs for quick access."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _bookmark_path(store_path: Path) -> Path:
    return store_path / ".bookmarks.json"


def _load_bookmarks(store_path: Path) -> dict:
    p = _bookmark_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_bookmarks(store_path: Path, data: dict) -> None:
    _bookmark_path(store_path).write_text(json.dumps(data, indent=2))


class BookmarkResult:
    def __init__(self, name: str, key: str, profile: str, ok: bool, message: str = ""):
        self.name = name
        self.key = key
        self.profile = profile
        self.ok = ok
        self.message = message

    def __repr__(self) -> str:
        return f"BookmarkResult(name={self.name!r}, key={self.key!r}, profile={self.profile!r}, ok={self.ok})"


def add_bookmark(
    store_path: Path, name: str, key: str, profile: str = "default"
) -> BookmarkResult:
    if not name or not name.strip():
        return BookmarkResult(name, key, profile, ok=False, message="Bookmark name must not be empty.")
    if not key or not key.strip():
        return BookmarkResult(name, key, profile, ok=False, message="Key must not be empty.")
    data = _load_bookmarks(store_path)
    data[name] = {"key": key, "profile": profile}
    _save_bookmarks(store_path, data)
    return BookmarkResult(name, key, profile, ok=True, message="Bookmark added.")


def get_bookmark(store_path: Path, name: str) -> Optional[dict]:
    data = _load_bookmarks(store_path)
    return data.get(name)


def remove_bookmark(store_path: Path, name: str) -> bool:
    data = _load_bookmarks(store_path)
    if name not in data:
        return False
    del data[name]
    _save_bookmarks(store_path, data)
    return True


def list_bookmarks(store_path: Path) -> list[dict]:
    data = _load_bookmarks(store_path)
    return [
        {"name": name, "key": entry["key"], "profile": entry["profile"]}
        for name, entry in sorted(data.items())
    ]
