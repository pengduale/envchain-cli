"""Boolean flag metadata for stored environment variables."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass


def _flag_path(store_path: str) -> Path:
    return Path(store_path).parent / "flags.json"


def _load_flags(store_path: str) -> dict:
    p = _flag_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_flags(store_path: str, data: dict) -> None:
    _flag_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class FlagResult:
    key: str
    flag: str
    value: bool
    action: str

    def __repr__(self) -> str:
        return f"<FlagResult {self.action} {self.key}.{self.flag}={self.value}>"


VALID_FLAGS = {"required", "sensitive", "readonly", "deprecated"}


def set_flag(store_path: str, key: str, flag: str, value: bool = True) -> FlagResult:
    if flag not in VALID_FLAGS:
        raise ValueError(f"Unknown flag '{flag}'. Valid flags: {sorted(VALID_FLAGS)}")
    data = _load_flags(store_path)
    entry = data.setdefault(key, {})
    entry[flag] = value
    _save_flags(store_path, data)
    return FlagResult(key=key, flag=flag, value=value, action="set")


def get_flag(store_path: str, key: str, flag: str) -> bool | None:
    if flag not in VALID_FLAGS:
        raise ValueError(f"Unknown flag '{flag}'. Valid flags: {sorted(VALID_FLAGS)}")
    data = _load_flags(store_path)
    return data.get(key, {}).get(flag)


def get_all_flags(store_path: str, key: str) -> dict:
    data = _load_flags(store_path)
    return dict(data.get(key, {}))


def remove_flag(store_path: str, key: str, flag: str) -> bool:
    data = _load_flags(store_path)
    if key in data and flag in data[key]:
        del data[key][flag]
        if not data[key]:
            del data[key]
        _save_flags(store_path, data)
        return True
    return False


def list_flagged(store_path: str, flag: str) -> list[str]:
    data = _load_flags(store_path)
    return [k for k, flags in data.items() if flags.get(flag) is True]
