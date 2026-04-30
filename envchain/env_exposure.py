"""Track and assess exposure risk for stored environment variables."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("none", "low", "medium", "high", "critical")


def _exposure_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_exposure.json"


def _load_exposure(store_path: Path) -> dict:
    p = _exposure_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_exposure(store_path: Path, data: dict) -> None:
    _exposure_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ExposureResult:
    ok: bool
    key: str
    level: Optional[str] = None
    surfaces: list[str] = field(default_factory=list)
    note: Optional[str] = None
    error: Optional[str] = None

    def __repr__(self) -> str:
        if not self.ok:
            return f"ExposureResult(error={self.error!r})"
        return (
            f"ExposureResult(key={self.key!r}, level={self.level!r}, "
            f"surfaces={self.surfaces!r})"
        )


def set_exposure(
    store_path: Path,
    key: str,
    level: str,
    surfaces: Optional[list[str]] = None,
    note: Optional[str] = None,
) -> ExposureResult:
    """Record the exposure level and surfaces for a key."""
    if not key:
        return ExposureResult(ok=False, key=key, error="Key must not be empty.")
    if level not in VALID_LEVELS:
        return ExposureResult(
            ok=False, key=key,
            error=f"Invalid level {level!r}. Choose from {VALID_LEVELS}."
        )
    data = _load_exposure(store_path)
    data[key] = {
        "level": level,
        "surfaces": surfaces or [],
        "note": note,
    }
    _save_exposure(store_path, data)
    return ExposureResult(ok=True, key=key, level=level,
                          surfaces=surfaces or [], note=note)


def get_exposure(store_path: Path, key: str) -> Optional[ExposureResult]:
    """Retrieve exposure info for a key, or None if not set."""
    data = _load_exposure(store_path)
    if key not in data:
        return None
    entry = data[key]
    return ExposureResult(
        ok=True, key=key,
        level=entry.get("level"),
        surfaces=entry.get("surfaces", []),
        note=entry.get("note"),
    )


def remove_exposure(store_path: Path, key: str) -> bool:
    """Remove exposure record for a key. Returns True if removed."""
    data = _load_exposure(store_path)
    if key not in data:
        return False
    del data[key]
    _save_exposure(store_path, data)
    return True


def list_exposure(store_path: Path) -> list[ExposureResult]:
    """Return all exposure records sorted by level severity."""
    data = _load_exposure(store_path)
    results = [
        ExposureResult(
            ok=True, key=k,
            level=v.get("level"),
            surfaces=v.get("surfaces", []),
            note=v.get("note"),
        )
        for k, v in data.items()
    ]
    results.sort(key=lambda r: VALID_LEVELS.index(r.level or "none"), reverse=True)
    return results
