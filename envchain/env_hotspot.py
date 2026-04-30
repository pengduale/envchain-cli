"""Track frequently accessed keys (hotspots) in the store."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _hotspot_path(store_dir: str) -> Path:
    return Path(store_dir) / ".envchain_hotspots.json"


def _load_hotspots(store_dir: str) -> Dict[str, int]:
    p = _hotspot_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_hotspots(store_dir: str, data: Dict[str, int]) -> None:
    _hotspot_path(store_dir).write_text(json.dumps(data, indent=2))


@dataclass
class HotspotResult:
    key: str
    count: int
    ok: bool = True
    error: Optional[str] = None

    def __repr__(self) -> str:
        if not self.ok:
            return f"HotspotResult(error={self.error!r})"
        return f"HotspotResult(key={self.key!r}, count={self.count})"


def record_access(store_dir: str, key: str) -> HotspotResult:
    """Increment the access counter for *key*."""
    if not key or not key.strip():
        return HotspotResult(key=key, count=0, ok=False, error="Key must not be empty")
    data = _load_hotspots(store_dir)
    data[key] = data.get(key, 0) + 1
    _save_hotspots(store_dir, data)
    return HotspotResult(key=key, count=data[key])


def get_count(store_dir: str, key: str) -> Optional[int]:
    """Return the access count for *key*, or None if never accessed."""
    return _load_hotspots(store_dir).get(key)


def top_keys(store_dir: str, n: int = 10) -> List[HotspotResult]:
    """Return the top *n* most-accessed keys, sorted descending."""
    data = _load_hotspots(store_dir)
    ranked = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
    return [HotspotResult(key=k, count=c) for k, c in ranked[:n]]


def reset_hotspots(store_dir: str) -> int:
    """Clear all hotspot data.  Returns the number of entries removed."""
    data = _load_hotspots(store_dir)
    count = len(data)
    _save_hotspots(store_dir, {})
    return count
