"""Maturity level tracking for environment variables."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("experimental", "beta", "stable", "deprecated", "retired")


def _maturity_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_maturity.json"


def _load_maturity(store_path: Path) -> dict:
    p = _maturity_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_maturity(store_path: Path, data: dict) -> None:
    _maturity_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class MaturityResult:
    key: str
    level: str
    note: Optional[str] = None
    ok: bool = True
    error: Optional[str] = None

    def __repr__(self) -> str:
        if not self.ok:
            return f"MaturityResult(error={self.error!r})"
        note_part = f", note={self.note!r}" if self.note else ""
        return f"MaturityResult(key={self.key!r}, level={self.level!r}{note_part})"


def set_maturity(store_path: Path, key: str, level: str, note: Optional[str] = None) -> MaturityResult:
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid maturity level {level!r}. Choose from: {VALID_LEVELS}")
    data = _load_maturity(store_path)
    data[key] = {"level": level, "note": note}
    _save_maturity(store_path, data)
    return MaturityResult(key=key, level=level, note=note)


def get_maturity(store_path: Path, key: str) -> Optional[MaturityResult]:
    data = _load_maturity(store_path)
    if key not in data:
        return None
    entry = data[key]
    return MaturityResult(key=key, level=entry["level"], note=entry.get("note"))


def remove_maturity(store_path: Path, key: str) -> bool:
    data = _load_maturity(store_path)
    if key not in data:
        return False
    del data[key]
    _save_maturity(store_path, data)
    return True


def list_maturity(store_path: Path) -> list[MaturityResult]:
    data = _load_maturity(store_path)
    return [
        MaturityResult(key=k, level=v["level"], note=v.get("note"))
        for k, v in data.items()
    ]


def filter_by_level(store_path: Path, level: str) -> list[MaturityResult]:
    return [r for r in list_maturity(store_path) if r.level == level]
