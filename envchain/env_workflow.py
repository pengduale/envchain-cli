"""Workflow support: define ordered sequences of keys that must be set together."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _workflow_path(store_path: str) -> Path:
    return Path(store_path).parent / ".envchain_workflows.json"


def _load_workflows(store_path: str) -> dict:
    p = _workflow_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_workflows(store_path: str, data: dict) -> None:
    _workflow_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class WorkflowResult:
    name: str
    keys: List[str]
    ok: bool
    message: str = ""

    def __repr__(self) -> str:
        return f"WorkflowResult(name={self.name!r}, keys={self.keys}, ok={self.ok})"


def create_workflow(store_path: str, name: str, keys: List[str]) -> WorkflowResult:
    """Define a named workflow with an ordered list of required keys."""
    if not name or not name.strip():
        return WorkflowResult(name=name, keys=keys, ok=False, message="Workflow name must not be empty.")
    if not keys:
        return WorkflowResult(name=name, keys=keys, ok=False, message="Workflow must contain at least one key.")
    data = _load_workflows(store_path)
    data[name] = keys
    _save_workflows(store_path, data)
    return WorkflowResult(name=name, keys=keys, ok=True, message="Workflow created.")


def get_workflow(store_path: str, name: str) -> Optional[List[str]]:
    """Return the ordered key list for a workflow, or None if not found."""
    data = _load_workflows(store_path)
    return data.get(name)


def delete_workflow(store_path: str, name: str) -> bool:
    """Remove a workflow by name. Returns True if removed, False if not found."""
    data = _load_workflows(store_path)
    if name not in data:
        return False
    del data[name]
    _save_workflows(store_path, data)
    return True


def list_workflows(store_path: str) -> List[str]:
    """Return all workflow names."""
    return list(_load_workflows(store_path).keys())


def validate_workflow(store_path: str, name: str, present_keys: List[str]) -> WorkflowResult:
    """Check that all keys in the workflow are present in the provided key list."""
    keys = get_workflow(store_path, name)
    if keys is None:
        return WorkflowResult(name=name, keys=[], ok=False, message=f"Workflow '{name}' not found.")
    missing = [k for k in keys if k not in present_keys]
    if missing:
        msg = "Missing keys: " + ", ".join(missing)
        return WorkflowResult(name=name, keys=keys, ok=False, message=msg)
    return WorkflowResult(name=name, keys=keys, ok=True, message="All workflow keys are present.")
