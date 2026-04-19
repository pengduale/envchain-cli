"""Promote variables from one profile to another with optional filtering."""

from dataclasses import dataclass
from typing import Optional
from envchain.profile import list_profile_keys, get_profile_variable, set_profile_variable


@dataclass
class PromoteResult:
    key: str
    source: str
    target: str
    skipped: bool
    reason: str = ""

    def __repr__(self):
        status = "skipped" if self.skipped else "promoted"
        return f"PromoteResult({self.key}: {self.source}->{self.target} [{status}])"


def promote_variable(
    store_path: str,
    key: str,
    source_profile: str,
    target_profile: str,
    passphrase: str,
    overwrite: bool = False,
) -> PromoteResult:
    value = get_profile_variable(store_path, source_profile, key, passphrase)
    if value is None:
        return PromoteResult(key, source_profile, target_profile, skipped=True, reason="not found in source")

    existing = get_profile_variable(store_path, target_profile, key, passphrase)
    if existing is not None and not overwrite:
        return PromoteResult(key, source_profile, target_profile, skipped=True, reason="already exists in target")

    set_profile_variable(store_path, target_profile, key, value, passphrase)
    return PromoteResult(key, source_profile, target_profile, skipped=False)


def promote_all(
    store_path: str,
    source_profile: str,
    target_profile: str,
    passphrase: str,
    overwrite: bool = False,
    keys: Optional[list] = None,
) -> list[PromoteResult]:
    available = list_profile_keys(store_path, source_profile)
    selected = keys if keys else available
    return [
        promote_variable(store_path, k, source_profile, target_profile, passphrase, overwrite)
        for k in selected
    ]
