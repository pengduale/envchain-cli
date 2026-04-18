"""Pre/post hooks for envchain operations."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Callable, Dict, List, Optional

HOOK_EVENTS = ("pre-set", "post-set", "pre-get", "post-get", "pre-delete", "post-delete")


def _hooks_path(store_dir: str) -> Path:
    return Path(store_dir) / ".hooks.json"


def _load_hooks(store_dir: str) -> Dict[str, List[str]]:
    p = _hooks_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_hooks(store_dir: str, hooks: Dict[str, List[str]]) -> None:
    _hooks_path(store_dir).write_text(json.dumps(hooks, indent=2))


def add_hook(store_dir: str, event: str, command: str) -> None:
    if event not in HOOK_EVENTS:
        raise ValueError(f"Unknown event '{event}'. Valid: {HOOK_EVENTS}")
    hooks = _load_hooks(store_dir)
    hooks.setdefault(event, [])
    if command not in hooks[event]:
        hooks[event].append(command)
    _save_hooks(store_dir, hooks)


def remove_hook(store_dir: str, event: str, command: str) -> bool:
    hooks = _load_hooks(store_dir)
    lst = hooks.get(event, [])
    if command not in lst:
        return False
    lst.remove(command)
    hooks[event] = lst
    _save_hooks(store_dir, hooks)
    return True


def list_hooks(store_dir: str, event: Optional[str] = None) -> Dict[str, List[str]]:
    hooks = _load_hooks(store_dir)
    if event:
        return {event: hooks.get(event, [])}
    return hooks


def fire_hook(store_dir: str, event: str, key: str) -> List[str]:
    """Run hooks for event; returns list of commands executed."""
    import subprocess
    hooks = _load_hooks(store_dir)
    cmds = hooks.get(event, [])
    executed = []
    for cmd in cmds:
        full = f"{cmd} {key}"
        subprocess.run(full, shell=True, check=False)
        executed.append(full)
    return executed
