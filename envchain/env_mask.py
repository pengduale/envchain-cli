"""Mask/unmask variables so their values are hidden in output."""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


def _mask_path(store_dir: str) -> Path:
    return Path(store_dir) / ".mask.json"


def _load_masks(store_dir: str) -> dict:
    p = _mask_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_masks(store_dir: str, data: dict) -> None:
    _mask_path(store_dir).write_text(json.dumps(data, indent=2))


@dataclass
class MaskResult:
    key: str
    masked: bool

    def __repr__(self) -> str:
        state = "masked" if self.masked else "unmasked"
        return f"<MaskResult {self.key}={state}>"


def mask_variable(store_dir: str, key: str) -> MaskResult:
    """Mark a variable as masked."""
    data = _load_masks(store_dir)
    data[key] = True
    _save_masks(store_dir, data)
    return MaskResult(key=key, masked=True)


def unmask_variable(store_dir: str, key: str) -> MaskResult:
    """Remove mask from a variable."""
    data = _load_masks(store_dir)
    data.pop(key, None)
    _save_masks(store_dir, data)
    return MaskResult(key=key, masked=False)


def is_masked(store_dir: str, key: str) -> bool:
    """Return True if the variable is masked."""
    return _load_masks(store_dir).get(key, False)


def list_masked(store_dir: str) -> list[str]:
    """Return all masked variable keys."""
    return [k for k, v in _load_masks(store_dir).items() if v]


def apply_mask(store_dir: str, key: str, value: str) -> str:
    """Return masked display value if key is masked, else original."""
    if is_masked(store_dir, key):
        return "****"
    return value
