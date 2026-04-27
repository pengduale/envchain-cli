"""Track deprecated environment variable keys with optional replacement suggestions."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


def _deprecation_path(store_path: Path) -> Path:
    return store_path / ".envchain_deprecations.json"


def _load_deprecations(store_path: Path) -> dict:
    p = _deprecation_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deprecations(store_path: Path, data: dict) -> None:
    _deprecation_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class DeprecationResult:
    key: str
    reason: str
    replacement: Optional[str]
    ok: bool

    def __repr__(self) -> str:
        repl = f" -> {self.replacement}" if self.replacement else ""
        status = "deprecated" if self.ok else "error"
        return f"DeprecationResult({self.key}{repl}, reason={self.reason!r}, status={status})"


def mark_deprecated(
    store_path: Path,
    key: str,
    reason: str,
    replacement: Optional[str] = None,
) -> DeprecationResult:
    """Mark a key as deprecated with a reason and optional replacement."""
    if not key:
        raise ValueError("key must not be empty")
    if not reason:
        raise ValueError("reason must not be empty")
    data = _load_deprecations(store_path)
    data[key] = {"reason": reason, "replacement": replacement}
    _save_deprecations(store_path, data)
    return DeprecationResult(key=key, reason=reason, replacement=replacement, ok=True)


def get_deprecation(store_path: Path, key: str) -> Optional[DeprecationResult]:
    """Return deprecation info for a key, or None if not deprecated."""
    data = _load_deprecations(store_path)
    if key not in data:
        return None
    entry = data[key]
    return DeprecationResult(
        key=key,
        reason=entry["reason"],
        replacement=entry.get("replacement"),
        ok=True,
    )


def remove_deprecation(store_path: Path, key: str) -> bool:
    """Remove a deprecation mark from a key. Returns True if removed."""
    data = _load_deprecations(store_path)
    if key not in data:
        return False
    del data[key]
    _save_deprecations(store_path, data)
    return True


def list_deprecated(store_path: Path) -> list[DeprecationResult]:
    """Return all deprecated keys."""
    data = _load_deprecations(store_path)
    return [
        DeprecationResult(
            key=k,
            reason=v["reason"],
            replacement=v.get("replacement"),
            ok=True,
        )
        for k, v in data.items()
    ]
