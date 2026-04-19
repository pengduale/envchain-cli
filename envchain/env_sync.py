"""Sync environment variables between profiles or stores."""
from pathlib import Path
from typing import Optional
from envchain.store import get_variable, set_variable, list_keys
from envchain.profile import get_profile_variable, set_profile_variable, list_profile_keys


class SyncResult:
    def __init__(self):
        self.copied: list[str] = []
        self.skipped: list[str] = []
        self.overwritten: list[str] = []

    def __repr__(self):
        return f"SyncResult(copied={self.copied}, skipped={self.skipped}, overwritten={self.overwritten})"


def sync_profiles(
    store_path: Path,
    src_profile: str,
    dst_profile: str,
    passphrase: str,
    overwrite: bool = False,
) -> SyncResult:
    """Copy all variables from src_profile into dst_profile."""
    result = SyncResult()
    keys = list_profile_keys(store_path, src_profile)
    for key in keys:
        value = get_profile_variable(store_path, src_profile, key, passphrase)
        existing = get_profile_variable(store_path, dst_profile, key, passphrase)
        if existing is not None and not overwrite:
            result.skipped.append(key)
            continue
        if existing is not None:
            result.overwritten.append(key)
        else:
            result.copied.append(key)
        set_profile_variable(store_path, dst_profile, key, value, passphrase)
    return result


def sync_profile_to_default(
    store_path: Path,
    src_profile: str,
    passphrase: str,
    overwrite: bool = False,
) -> SyncResult:
    """Copy all variables from a named profile into the default store."""
    result = SyncResult()
    keys = list_profile_keys(store_path, src_profile)
    for key in keys:
        value = get_profile_variable(store_path, src_profile, key, passphrase)
        existing = get_variable(store_path, key, passphrase)
        if existing is not None and not overwrite:
            result.skipped.append(key)
            continue
        if existing is not None:
            result.overwritten.append(key)
        else:
            result.copied.append(key)
        set_variable(store_path, key, value, passphrase)
    return result
