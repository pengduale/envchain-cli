"""Sensitivity level management for stored environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("low", "medium", "high", "critical")


def _sensitivity_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_sensitivity.json"


def _load_sensitivity(store_path: Path) -> dict:
    path = _sensitivity_path(store_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_sensitivity(store_path: Path, data: dict) -> None:
    _sensitivity_path(store_path).write_text(json.dumps(data, indent=2))


class SensitivityResult:
    def __init__(self, key: str, level: str, ok: bool, message: str = ""):
        self.key = key
        self.level = level
        self.ok = ok
        self.message = message

    def __repr__(self) -> str:
        return f"SensitivityResult(key={self.key!r}, level={self.level!r}, ok={self.ok})"


def set_sensitivity(store_path: Path, key: str, level: str) -> SensitivityResult:
    if level not in VALID_LEVELS:
        raise ValueError(f"Invalid sensitivity level {level!r}. Choose from: {VALID_LEVELS}")
    data = _load_sensitivity(store_path)
    data[key] = level
    _save_sensitivity(store_path, data)
    return SensitivityResult(key=key, level=level, ok=True, message=f"Set sensitivity for {key!r} to {level!r}")


def get_sensitivity(store_path: Path, key: str) -> Optional[str]:
    data = _load_sensitivity(store_path)
    return data.get(key)


def remove_sensitivity(store_path: Path, key: str) -> bool:
    data = _load_sensitivity(store_path)
    if key not in data:
        return False
    del data[key]
    _save_sensitivity(store_path, data)
    return True


def list_sensitivity(store_path: Path) -> dict:
    return _load_sensitivity(store_path)


def get_keys_by_level(store_path: Path, level: str) -> list:
    data = _load_sensitivity(store_path)
    return [k for k, v in data.items() if v == level]
