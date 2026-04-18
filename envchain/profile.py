"""Profile support: named groups of environment variables."""
from __future__ import annotations

from pathlib import Path
from typing import List

from envchain.store import set_variable, get_variable, delete_variable, list_keys


DEFAULT_PROFILE = "default"


def _profile_store_path(base_path: Path, profile: str) -> Path:
    """Return a store path scoped to a profile."""
    return base_path.parent / f"{base_path.stem}.{profile}.json"


def list_profiles(base_path: Path) -> List[str]:
    """Return all profile names found alongside base_path."""
    stem = base_path.stem
    profiles = []
    for f in base_path.parent.glob(f"{stem}.*.json"):
        parts = f.stem.split(".")
        if len(parts) >= 2:
            profiles.append(parts[-1])
    if base_path.exists():
        profiles.insert(0, DEFAULT_PROFILE)
    return sorted(set(profiles))


def set_profile_variable(base_path: Path, profile: str, key: str, value: str, passphrase: str) -> None:
    store_path = base_path if profile == DEFAULT_PROFILE else _profile_store_path(base_path, profile)
    set_variable(store_path, key, value, passphrase)


def get_profile_variable(base_path: Path, profile: str, key: str, passphrase: str) -> str:
    store_path = base_path if profile == DEFAULT_PROFILE else _profile_store_path(base_path, profile)
    return get_variable(store_path, key, passphrase)


def delete_profile_variable(base_path: Path, profile: str, key: str, passphrase: str) -> None:
    store_path = base_path if profile == DEFAULT_PROFILE else _profile_store_path(base_path, profile)
    delete_variable(store_path, key, passphrase)


def list_profile_keys(base_path: Path, profile: str, passphrase: str) -> List[str]:
    store_path = base_path if profile == DEFAULT_PROFILE else _profile_store_path(base_path, profile)
    return list_keys(store_path, passphrase)
