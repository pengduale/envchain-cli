"""Pin variables to specific versions (snapshots) for reproducibility."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from typing import Optional


@dataclass
class PinResult:
    key: str
    profile: str
    snapshot_id: str
    success: bool
    message: str = ""

    def __repr__(self) -> str:
        status = "pinned" if self.success else "failed"
        return f"<PinResult {self.key}@{self.profile} -> {self.snapshot_id} [{status}]>"


def _pin_path(store_path: Path) -> Path:
    return store_path / ".pins.json"


def _load_pins(store_path: Path) -> dict:
    p = _pin_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_pins(store_path: Path, pins: dict) -> None:
    _pin_path(store_path).write_text(json.dumps(pins, indent=2))


def pin_variable(store_path: Path, key: str, snapshot_id: str, profile: str = "default") -> PinResult:
    pins = _load_pins(store_path)
    ns = pins.setdefault(profile, {})
    ns[key] = snapshot_id
    _save_pins(store_path, pins)
    return PinResult(key=key, profile=profile, snapshot_id=snapshot_id, success=True)


def unpin_variable(store_path: Path, key: str, profile: str = "default") -> PinResult:
    pins = _load_pins(store_path)
    ns = pins.get(profile, {})
    if key not in ns:
        return PinResult(key=key, profile=profile, snapshot_id="", success=False, message="not pinned")
    snapshot_id = ns.pop(key)
    _save_pins(store_path, pins)
    return PinResult(key=key, profile=profile, snapshot_id=snapshot_id, success=True)


def get_pin(store_path: Path, key: str, profile: str = "default") -> Optional[str]:
    pins = _load_pins(store_path)
    return pins.get(profile, {}).get(key)


def list_pins(store_path: Path, profile: str = "default") -> dict[str, str]:
    pins = _load_pins(store_path)
    return dict(pins.get(profile, {}))
