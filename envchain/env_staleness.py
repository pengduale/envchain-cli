"""Staleness tracking: flag variables that haven't been updated in N days."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _staleness_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_staleness.json"


def _load_staleness(store_path: Path) -> dict:
    p = _staleness_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_staleness(store_path: Path, data: dict) -> None:
    _staleness_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class StalenessResult:
    key: str
    last_updated: float
    threshold_days: int
    is_stale: bool
    age_days: float

    def __repr__(self) -> str:
        status = "STALE" if self.is_stale else "fresh"
        return f"<StalenessResult key={self.key!r} age_days={self.age_days:.1f} status={status}>"


def touch_key(store_path: Path, key: str) -> StalenessResult:
    """Record the current time as the last-updated timestamp for key."""
    data = _load_staleness(store_path)
    now = time.time()
    entry = data.get(key, {})
    entry["last_updated"] = now
    threshold = entry.get("threshold_days", 30)
    data[key] = entry
    _save_staleness(store_path, data)
    return StalenessResult(
        key=key,
        last_updated=now,
        threshold_days=threshold,
        is_stale=False,
        age_days=0.0,
    )


def set_threshold(store_path: Path, key: str, days: int) -> StalenessResult:
    """Set the staleness threshold (in days) for a key."""
    if days <= 0:
        raise ValueError("threshold_days must be a positive integer")
    data = _load_staleness(store_path)
    entry = data.get(key, {})
    entry["threshold_days"] = days
    data[key] = entry
    _save_staleness(store_path, data)
    last_updated = entry.get("last_updated", 0.0)
    age_days = (time.time() - last_updated) / 86400 if last_updated else float("inf")
    return StalenessResult(
        key=key,
        last_updated=last_updated,
        threshold_days=days,
        is_stale=age_days > days,
        age_days=age_days,
    )


def check_staleness(store_path: Path, key: str) -> Optional[StalenessResult]:
    """Return staleness info for a key, or None if no record exists."""
    data = _load_staleness(store_path)
    if key not in data:
        return None
    entry = data[key]
    last_updated = entry.get("last_updated", 0.0)
    threshold = entry.get("threshold_days", 30)
    age_days = (time.time() - last_updated) / 86400 if last_updated else float("inf")
    return StalenessResult(
        key=key,
        last_updated=last_updated,
        threshold_days=threshold,
        is_stale=age_days > threshold,
        age_days=age_days,
    )


def list_stale(store_path: Path) -> list[StalenessResult]:
    """Return all keys whose age exceeds their configured threshold."""
    data = _load_staleness(store_path)
    results = []
    now = time.time()
    for key, entry in data.items():
        last_updated = entry.get("last_updated", 0.0)
        threshold = entry.get("threshold_days", 30)
        age_days = (now - last_updated) / 86400 if last_updated else float("inf")
        if age_days > threshold:
            results.append(StalenessResult(
                key=key,
                last_updated=last_updated,
                threshold_days=threshold,
                is_stale=True,
                age_days=age_days,
            ))
    return results
