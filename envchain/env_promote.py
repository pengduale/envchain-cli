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
    """Promote a single variable from source_profile to target_profile.

    Args:
        store_path: Path to the envchain store.
        key: The variable key to promote.
        source_profile: Profile to read the variable from.
        target_profile: Profile to write the variable to.
        passphrase: Passphrase used to decrypt/encrypt the store.
        overwrite: If True, overwrite the variable if it already exists in target.

    Returns:
        A PromoteResult indicating whether the variable was promoted or skipped.
    """
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
    """Promote all (or a subset of) variables from source_profile to target_profile.

    Args:
        store_path: Path to the envchain store.
        source_profile: Profile to read variables from.
        target_profile: Profile to write variables to.
        passphrase: Passphrase used to decrypt/encrypt the store.
        overwrite: If True, overwrite variables that already exist in target.
        keys: Optional list of keys to promote. If None, all keys in source are used.

    Returns:
        A list of PromoteResult objects, one per key processed.

    Raises:
        ValueError: If keys are specified that do not exist in the source profile.
    """
    available = list_profile_keys(store_path, source_profile)

    if keys:
        missing = [k for k in keys if k not in available]
        if missing:
            raise ValueError(
                f"Keys not found in source profile '{source_profile}': {', '.join(missing)}"
            )
        selected = keys
    else:
        selected = available

    return [
        promote_variable(store_path, k, source_profile, target_profile, passphrase, overwrite)
        for k in selected
    ]
