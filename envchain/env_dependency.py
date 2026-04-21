"""Track dependencies between environment variables."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


def _dep_path(store_path: Path) -> Path:
    return store_path.parent / "dependencies.json"


def _load_deps(store_path: Path) -> Dict[str, List[str]]:
    p = _dep_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_deps(store_path: Path, data: Dict[str, List[str]]) -> None:
    _dep_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class DependencyResult:
    key: str
    depends_on: List[str]
    ok: bool
    message: str = ""

    def __repr__(self) -> str:
        return f"DependencyResult(key={self.key!r}, depends_on={self.depends_on}, ok={self.ok})"


def add_dependency(store_path: Path, key: str, depends_on: str) -> DependencyResult:
    """Record that *key* depends on *depends_on*."""
    if not key or not depends_on:
        raise ValueError("key and depends_on must be non-empty strings")
    data = _load_deps(store_path)
    deps = data.setdefault(key, [])
    if depends_on not in deps:
        deps.append(depends_on)
    _save_deps(store_path, data)
    return DependencyResult(key=key, depends_on=deps, ok=True, message="dependency added")


def remove_dependency(store_path: Path, key: str, depends_on: str) -> bool:
    """Remove a single dependency edge. Returns True if it existed."""
    data = _load_deps(store_path)
    deps = data.get(key, [])
    if depends_on not in deps:
        return False
    deps.remove(depends_on)
    if not deps:
        del data[key]
    _save_deps(store_path, data)
    return True


def get_dependencies(store_path: Path, key: str) -> List[str]:
    """Return the list of keys that *key* depends on."""
    return _load_deps(store_path).get(key, [])


def list_all_dependencies(store_path: Path) -> Dict[str, List[str]]:
    """Return the full dependency map."""
    return dict(_load_deps(store_path))


def check_dependencies(store_path: Path, key: str, present_keys: List[str]) -> DependencyResult:
    """Check whether all dependencies of *key* are satisfied by *present_keys*."""
    deps = get_dependencies(store_path, key)
    missing = [d for d in deps if d not in present_keys]
    if missing:
        return DependencyResult(
            key=key,
            depends_on=deps,
            ok=False,
            message=f"missing dependencies: {', '.join(missing)}",
        )
    return DependencyResult(key=key, depends_on=deps, ok=True, message="all dependencies satisfied")
