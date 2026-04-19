"""Per-variable description/documentation storage."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


def _desc_path(store_dir: str) -> Path:
    return Path(store_dir) / ".descriptions.json"


def _load_descriptions(store_dir: str) -> dict:
    p = _desc_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_descriptions(store_dir: str, data: dict) -> None:
    p = _desc_path(store_dir)
    p.write_text(json.dumps(data, indent=2))


@dataclass
class DescriptionResult:
    key: str
    description: str | None
    ok: bool

    def __repr__(self) -> str:
        return f"<DescriptionResult key={self.key!r} ok={self.ok}>"


def set_description(store_dir: str, key: str, description: str) -> DescriptionResult:
    if not key:
        raise ValueError("Key must not be empty")
    data = _load_descriptions(store_dir)
    data[key] = description
    _save_descriptions(store_dir, data)
    return DescriptionResult(key=key, description=description, ok=True)


def get_description(store_dir: str, key: str) -> str | None:
    data = _load_descriptions(store_dir)
    return data.get(key)


def remove_description(store_dir: str, key: str) -> bool:
    data = _load_descriptions(store_dir)
    if key not in data:
        return False
    del data[key]
    _save_descriptions(store_dir, data)
    return True


def list_descriptions(store_dir: str) -> dict[str, str]:
    return dict(_load_descriptions(store_dir))
