"""Rename environment variable keys across profiles."""
from dataclasses import dataclass
from typing import Optional
from envchain.store import get_variable, set_variable, delete_variable, list_keys
from envchain.profile import get_profile_variable, set_profile_variable, delete_profile_variable, list_profile_keys


@dataclass
class RenameResult:
    old_key: str
    new_key: str
    profile: Optional[str]
    success: bool
    reason: str = ""

    def __repr__(self):
        tag = f"[{self.profile}]" if self.profile else "[default]"
        status = "ok" if self.success else f"skip({self.reason})"
        return f"RenameResult({tag} {self.old_key} -> {self.new_key}: {status})"


def rename_variable(store_path, old_key: str, new_key: str, passphrase: str,
                    profile: Optional[str] = None, overwrite: bool = False) -> RenameResult:
    """Rename a single variable, optionally in a named profile."""
    if profile:
        value = get_profile_variable(store_path, profile, old_key, passphrase)
    else:
        value = get_variable(store_path, old_key, passphrase)

    if value is None:
        return RenameResult(old_key, new_key, profile, False, "source key not found")

    if not overwrite:
        if profile:
            existing = get_profile_variable(store_path, profile, new_key, passphrase)
        else:
            existing = get_variable(store_path, new_key, passphrase)
        if existing is not None:
            return RenameResult(old_key, new_key, profile, False, "destination key exists")

    if profile:
        set_profile_variable(store_path, profile, new_key, value, passphrase)
        delete_profile_variable(store_path, profile, old_key)
    else:
        set_variable(store_path, new_key, value, passphrase)
        delete_variable(store_path, old_key)

    return RenameResult(old_key, new_key, profile, True)


def rename_all_profiles(store_path, old_key: str, new_key: str, passphrase: str,
                        profiles: list, overwrite: bool = False) -> list:
    """Rename a key across multiple profiles."""
    results = []
    for profile in profiles:
        r = rename_variable(store_path, old_key, new_key, passphrase, profile=profile, overwrite=overwrite)
        results.append(r)
    return results
