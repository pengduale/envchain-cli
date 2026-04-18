"""Tag-based grouping for environment variables."""
from __future__ import annotations
from typing import Dict, List
from envchain.store import _load_raw, _save_raw

TAGS_KEY = "__tags__"


def _load_tags(store_path: str) -> Dict[str, List[str]]:
    data = _load_raw(store_path)
    return data.get(TAGS_KEY, {})


def _save_tags(store_path: str, tags: Dict[str, List[str]]) -> None:
    data = _load_raw(store_path)
    data[TAGS_KEY] = tags
    _save_raw(store_path, data)


def tag_variable(store_path: str, key: str, tag: str) -> None:
    """Add a tag to a variable."""
    tags = _load_tags(store_path)
    tags.setdefault(key, [])
    if tag not in tags[key]:
        tags[key].append(tag)
    _save_tags(store_path, tags)


def untag_variable(store_path: str, key: str, tag: str) -> None:
    """Remove a tag from a variable."""
    tags = _load_tags(store_path)
    if key in tags:
        tags[key] = [t for t in tags[key] if t != tag]
        if not tags[key]:
            del tags[key]
    _save_tags(store_path, tags)


def get_tags(store_path: str, key: str) -> List[str]:
    """Return tags for a given variable key."""
    return _load_tags(store_path).get(key, [])


def list_by_tag(store_path: str, tag: str) -> List[str]:
    """Return all variable keys that have the given tag."""
    tags = _load_tags(store_path)
    return [key for key, key_tags in tags.items() if tag in key_tags]


def all_tags(store_path: str) -> Dict[str, List[str]]:
    """Return full tag mapping."""
    return _load_tags(store_path)
