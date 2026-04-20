"""Category management for environment variables."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path


def _category_path(store_dir: str) -> Path:
    return Path(store_dir) / ".categories.json"


def _load_categories(store_dir: str) -> dict[str, str]:
    p = _category_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_categories(store_dir: str, data: dict[str, str]) -> None:
    _category_path(store_dir).write_text(json.dumps(data, indent=2))


@dataclass
class CategoryResult:
    key: str
    category: str
    success: bool
    message: str = ""

    def __repr__(self) -> str:
        return f"<CategoryResult key={self.key!r} category={self.category!r} success={self.success}>"


def set_category(store_dir: str, key: str, category: str) -> CategoryResult:
    if not key:
        return CategoryResult(key=key, category=category, success=False, message="Key must not be empty.")
    if not category:
        return CategoryResult(key=key, category=category, success=False, message="Category must not be empty.")
    data = _load_categories(store_dir)
    data[key] = category
    _save_categories(store_dir, data)
    return CategoryResult(key=key, category=category, success=True)


def get_category(store_dir: str, key: str) -> str | None:
    return _load_categories(store_dir).get(key)


def remove_category(store_dir: str, key: str) -> bool:
    data = _load_categories(store_dir)
    if key not in data:
        return False
    del data[key]
    _save_categories(store_dir, data)
    return True


def list_by_category(store_dir: str) -> dict[str, list[str]]:
    data = _load_categories(store_dir)
    result: dict[str, list[str]] = {}
    for key, cat in data.items():
        result.setdefault(cat, []).append(key)
    return result


def list_categories(store_dir: str) -> list[str]:
    return sorted(set(_load_categories(store_dir).values()))
