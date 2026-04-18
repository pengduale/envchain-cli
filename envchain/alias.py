"""Variable aliasing: map short alias names to full variable keys."""
from __future__ import annotations
import json
from pathlib import Path


def _alias_path(store_dir: str) -> Path:
    return Path(store_dir) / ".aliases.json"


def _load_aliases(store_dir: str) -> dict[str, str]:
    p = _alias_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_aliases(store_dir: str, aliases: dict[str, str]) -> None:
    _alias_path(store_dir).write_text(json.dumps(aliases, indent=2))


def set_alias(store_dir: str, alias: str, key: str) -> None:
    """Create or update an alias pointing to key."""
    aliases = _load_aliases(store_dir)
    aliases[alias] = key
    _save_aliases(store_dir, aliases)


def remove_alias(store_dir: str, alias: str) -> None:
    """Remove an alias. Raises KeyError if not found."""
    aliases = _load_aliases(store_dir)
    if alias not in aliases:
        raise KeyError(f"Alias '{alias}' not found")
    del aliases[alias]
    _save_aliases(store_dir, aliases)


def resolve_alias(store_dir: str, alias: str) -> str | None:
    """Return the key an alias points to, or None."""
    return _load_aliases(store_dir).get(alias)


def list_aliases(store_dir: str) -> dict[str, str]:
    """Return all aliases as {alias: key}."""
    return _load_aliases(store_dir)
