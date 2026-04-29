"""Track the origin/source of environment variables (e.g., manual, imported, synced)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VALID_SOURCES = {"manual", "imported", "synced", "generated", "migrated"}


def _source_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_sources.json"


def _load_sources(store_path: Path) -> dict:
    p = _source_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_sources(store_path: Path, data: dict) -> None:
    _source_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class SourceResult:
    key: str
    source: str
    note: Optional[str]
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        if self.ok:
            return f"<SourceResult key={self.key!r} source={self.source!r}>"
        return f"<SourceResult key={self.key!r} error={self.error!r}>"


def set_source(store_path: Path, key: str, source: str, note: Optional[str] = None) -> SourceResult:
    if source not in VALID_SOURCES:
        return SourceResult(key=key, source=source, note=note, ok=False,
                            error=f"Invalid source '{source}'. Valid: {sorted(VALID_SOURCES)}")
    data = _load_sources(store_path)
    data[key] = {"source": source, "note": note}
    _save_sources(store_path, data)
    return SourceResult(key=key, source=source, note=note, ok=True)


def get_source(store_path: Path, key: str) -> Optional[SourceResult]:
    data = _load_sources(store_path)
    if key not in data:
        return None
    entry = data[key]
    return SourceResult(key=key, source=entry["source"], note=entry.get("note"), ok=True)


def remove_source(store_path: Path, key: str) -> bool:
    data = _load_sources(store_path)
    if key not in data:
        return False
    del data[key]
    _save_sources(store_path, data)
    return True


def list_sources(store_path: Path) -> list[SourceResult]:
    data = _load_sources(store_path)
    return [
        SourceResult(key=k, source=v["source"], note=v.get("note"), ok=True)
        for k, v in data.items()
    ]
