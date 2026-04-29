"""Classification system for environment variables (e.g. public, internal, confidential, secret)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_LEVELS = ("public", "internal", "confidential", "secret")


def _classification_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_classification.json"


def _load_classifications(store_path: str) -> dict:
    p = _classification_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_classifications(store_path: str, data: dict) -> None:
    _classification_path(store_path).write_text(json.dumps(data, indent=2))


class ClassificationResult:
    def __init__(self, ok: bool, key: str, level: Optional[str] = None, message: str = ""):
        self.ok = ok
        self.key = key
        self.level = level
        self.message = message

    def __repr__(self) -> str:
        return f"ClassificationResult(ok={self.ok}, key={self.key!r}, level={self.level!r})"


def set_classification(store_path: str, key: str, level: str) -> ClassificationResult:
    if level not in VALID_LEVELS:
        return ClassificationResult(
            ok=False, key=key, message=f"Invalid level {level!r}. Choose from {VALID_LEVELS}."
        )
    data = _load_classifications(store_path)
    data[key] = level
    _save_classifications(store_path, data)
    return ClassificationResult(ok=True, key=key, level=level)


def get_classification(store_path: str, key: str) -> Optional[str]:
    return _load_classifications(store_path).get(key)


def remove_classification(store_path: str, key: str) -> bool:
    data = _load_classifications(store_path)
    if key not in data:
        return False
    del data[key]
    _save_classifications(store_path, data)
    return True


def list_classifications(store_path: str) -> dict:
    return dict(_load_classifications(store_path))
