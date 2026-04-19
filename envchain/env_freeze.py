"""Freeze: snapshot current live env vars matching stored keys into a locked record."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envchain.store import list_keys, set_variable, get_variable
from envchain.profile import _profile_store_path


@dataclass
class FreezeResult:
    frozen: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    profile: str = "default"
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return (
            f"FreezeResult(profile={self.profile!r}, "
            f"frozen={len(self.frozen)}, skipped={len(self.skipped)})"
        )


def freeze_from_env(
    store_path: Path,
    passphrase: str,
    *,
    profile: str = "default",
    prefix: Optional[str] = None,
    overwrite: bool = False,
    keys: Optional[list[str]] = None,
) -> FreezeResult:
    """Read values from the live OS environment and store them encrypted.

    Args:
        store_path: base store directory.
        passphrase: encryption passphrase.
        profile: target profile name.
        prefix: if set, only consider env vars with this prefix.
        overwrite: replace existing stored values when True.
        keys: explicit list of keys to freeze; overrides prefix filter.
    """
    result = FreezeResult(profile=profile)

    if profile == "default":
        target_path = store_path
    else:
        target_path = _profile_store_path(store_path, profile)

    existing = set(list_keys(target_path))

    candidates: list[str]
    if keys is not None:
        candidates = keys
    else:
        candidates = [
            k for k in os.environ
            if (prefix is None or k.startswith(prefix))
        ]

    for key in candidates:
        value = os.environ.get(key)
        if value is None:
            result.skipped.append(key)
            continue
        if key in existing and not overwrite:
            result.skipped.append(key)
            continue
        set_variable(target_path, key, value, passphrase)
        result.frozen.append(key)

    return result


def thaw_to_env(store_path: Path, passphrase: str, *, profile: str = "default") -> dict[str, str]:
    """Return a dict of all stored vars for the profile, ready to inject into env."""
    if profile == "default":
        target_path = store_path
    else:
        target_path = _profile_store_path(store_path, profile)

    result: dict[str, str] = {}
    for key in list_keys(target_path):
        value = get_variable(target_path, key, passphrase)
        if value is not None:
            result[key] = value
    return result
