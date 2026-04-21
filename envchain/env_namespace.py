"""Namespace support for grouping environment variables under logical prefixes."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


def _namespace_path(store_path: Path) -> Path:
    return store_path.parent / "namespaces.json"


def _load_namespaces(store_path: Path) -> dict:
    p = _namespace_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_namespaces(store_path: Path, data: dict) -> None:
    _namespace_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class NamespaceResult:
    ok: bool
    namespace: str
    key: str
    action: str

    def __repr__(self) -> str:
        return f"<NamespaceResult {self.action} {self.namespace}:{self.key} ok={self.ok}>"


def assign_namespace(store_path: Path, key: str, namespace: str) -> NamespaceResult:
    """Assign a key to a namespace."""
    if not namespace.strip():
        raise ValueError("Namespace must not be empty.")
    data = _load_namespaces(store_path)
    data[key] = namespace
    _save_namespaces(store_path, data)
    return NamespaceResult(ok=True, namespace=namespace, key=key, action="assign")


def get_namespace(store_path: Path, key: str) -> Optional[str]:
    """Return the namespace assigned to a key, or None."""
    return _load_namespaces(store_path).get(key)


def remove_namespace(store_path: Path, key: str) -> bool:
    """Remove a key's namespace assignment. Returns True if removed."""
    data = _load_namespaces(store_path)
    if key not in data:
        return False
    del data[key]
    _save_namespaces(store_path, data)
    return True


def list_keys_in_namespace(store_path: Path, namespace: str) -> list[str]:
    """Return all keys assigned to the given namespace."""
    data = _load_namespaces(store_path)
    return [k for k, ns in data.items() if ns == namespace]


def list_namespaces(store_path: Path) -> list[str]:
    """Return all distinct namespace names in use."""
    data = _load_namespaces(store_path)
    return sorted(set(data.values()))
