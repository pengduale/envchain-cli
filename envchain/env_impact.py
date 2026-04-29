"""Track and assess the impact level of environment variables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("low", "medium", "high", "critical")


def _impact_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_impact.json"


def _load_impact(store_path: Path) -> dict:
    p = _impact_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_impact(store_path: Path, data: dict) -> None:
    _impact_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class ImpactResult:
    key: str
    level: str
    reason: Optional[str]
    ok: bool
    error: Optional[str] = None

    def __repr__(self) -> str:
        if not self.ok:
            return f"ImpactResult(error={self.error!r})"
        return f"ImpactResult(key={self.key!r}, level={self.level!r})"


def set_impact(store_path: Path, key: str, level: str, reason: Optional[str] = None) -> ImpactResult:
    if level not in VALID_LEVELS:
        return ImpactResult(key=key, level=level, reason=reason, ok=False,
                            error=f"Invalid level {level!r}. Choose from {VALID_LEVELS}.")
    data = _load_impact(store_path)
    data[key] = {"level": level, "reason": reason}
    _save_impact(store_path, data)
    return ImpactResult(key=key, level=level, reason=reason, ok=True)


def get_impact(store_path: Path, key: str) -> Optional[ImpactResult]:
    data = _load_impact(store_path)
    if key not in data:
        return None
    entry = data[key]
    return ImpactResult(key=key, level=entry["level"], reason=entry.get("reason"), ok=True)


def remove_impact(store_path: Path, key: str) -> bool:
    data = _load_impact(store_path)
    if key not in data:
        return False
    del data[key]
    _save_impact(store_path, data)
    return True


def list_by_level(store_path: Path, level: str) -> list[ImpactResult]:
    data = _load_impact(store_path)
    return [
        ImpactResult(key=k, level=v["level"], reason=v.get("reason"), ok=True)
        for k, v in data.items()
        if v["level"] == level
    ]
