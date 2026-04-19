"""Copy variables between profiles or stores."""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

from envchain.store import get_variable, set_variable, list_keys
from envchain.profile import get_profile_variable, set_profile_variable, list_profile_keys


@dataclass
class CopyResult:
    copied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    overwritten: List[str] = field(default_factory=list)

    def __repr__(self):
        return (
            f"CopyResult(copied={len(self.copied)}, "
            f"skipped={len(self.skipped)}, overwritten={len(self.overwritten)})"
        )


def copy_profile_to_profile(
    store_path: Path,
    src_profile: str,
    dst_profile: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> CopyResult:
    """Copy variables from one profile to another."""
    result = CopyResult()
    all_keys = keys or list_profile_keys(store_path, src_profile)
    for key in all_keys:
        value = get_profile_variable(store_path, src_profile, key, passphrase)
        if value is None:
            result.skipped.append(key)
            continue
        existing = get_profile_variable(store_path, dst_profile, key, passphrase)
        if existing is not None and not overwrite:
            result.skipped.append(key)
            continue
        set_profile_variable(store_path, dst_profile, key, value, passphrase)
        if existing is not None:
            result.overwritten.append(key)
        else:
            result.copied.append(key)
    return result


def copy_default_to_profile(
    store_path: Path,
    dst_profile: str,
    passphrase: str,
    keys: Optional[List[str]] = None,
    overwrite: bool = False,
) -> CopyResult:
    """Copy variables from default store to a named profile."""
    result = CopyResult()
    all_keys = keys or list_keys(store_path)
    for key in all_keys:
        value = get_variable(store_path, key, passphrase)
        if value is None:
            result.skipped.append(key)
            continue
        existing = get_profile_variable(store_path, dst_profile, key, passphrase)
        if existing is not None and not overwrite:
            result.skipped.append(key)
            continue
        set_profile_variable(store_path, dst_profile, key, value, passphrase)
        if existing is not None:
            result.overwritten.append(key)
        else:
            result.copied.append(key)
    return result
