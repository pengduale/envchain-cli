"""Risk scoring for stored environment variables."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

VALID_LEVELS = ("low", "medium", "high", "critical")


def _risk_path(store_path: Path) -> Path:
    return store_path / ".envchain_risk.json"


def _load_risk(store_path: Path) -> dict:
    p = _risk_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_risk(store_path: Path, data: dict) -> None:
    _risk_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class RiskResult:
    ok: bool
    key: str
    level: Optional[str] = None
    reason: Optional[str] = None
    error: Optional[str] = None

    def __repr__(self) -> str:
        if not self.ok:
            return f"RiskResult(error={self.error!r})"
        return f"RiskResult(key={self.key!r}, level={self.level!r})"


def set_risk(store_path: Path, key: str, level: str, reason: str = "") -> RiskResult:
    if not key:
        return RiskResult(ok=False, key=key, error="key must not be empty")
    if level not in VALID_LEVELS:
        return RiskResult(ok=False, key=key, error=f"invalid level {level!r}; choose from {VALID_LEVELS}")
    data = _load_risk(store_path)
    data[key] = {"level": level, "reason": reason}
    _save_risk(store_path, data)
    return RiskResult(ok=True, key=key, level=level, reason=reason)


def get_risk(store_path: Path, key: str) -> Optional[RiskResult]:
    data = _load_risk(store_path)
    if key not in data:
        return None
    entry = data[key]
    return RiskResult(ok=True, key=key, level=entry["level"], reason=entry.get("reason", ""))


def remove_risk(store_path: Path, key: str) -> bool:
    data = _load_risk(store_path)
    if key not in data:
        return False
    del data[key]
    _save_risk(store_path, data)
    return True


def list_risk(store_path: Path) -> List[RiskResult]:
    data = _load_risk(store_path)
    return [
        RiskResult(ok=True, key=k, level=v["level"], reason=v.get("reason", ""))
        for k, v in data.items()
    ]
