"""Attach human-readable labels (descriptions) to stored variables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _label_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_labels.json"


def _load_labels(store_path: str) -> dict:
    p = _label_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_labels(store_path: str, data: dict) -> None:
    _label_path(store_path).write_text(json.dumps(data, indent=2))


def set_label(store_path: str, key: str, label: str) -> None:
    """Attach a label/description to a variable key."""
    data = _load_labels(store_path)
    data[key] = label
    _save_labels(store_path, data)


def get_label(store_path: str, key: str) -> Optional[str]:
    """Return the label for a key, or None if not set."""
    return _load_labels(store_path).get(key)


def remove_label(store_path: str, key: str) -> bool:
    """Remove the label for a key. Returns True if it existed."""
    data = _load_labels(store_path)
    if key not in data:
        return False
    del data[key]
    _save_labels(store_path, data)
    return True


def list_labels(store_path: str) -> dict[str, str]:
    """Return all key -> label mappings."""
    return dict(_load_labels(store_path))


def search_labels(store_path: str, query: str) -> dict[str, str]:
    """Return keys whose label contains the query string (case-insensitive)."""
    q = query.lower()
    return {k: v for k, v in _load_labels(store_path).items() if q in v.lower()}
