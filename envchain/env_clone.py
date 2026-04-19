"""Clone all variables from one profile to a new profile."""
from dataclasses import dataclass
from typing import Optional
from envchain.profile import list_profiles, set_profile_variable, get_profile_variable, list_profile_keys


@dataclass
class CloneResult:
    source: str
    destination: str
    copied: int
    skipped: int
    overwritten: int

    def __repr__(self) -> str:
        return (
            f"CloneResult(source={self.source!r}, destination={self.destination!r}, "
            f"copied={self.copied}, skipped={self.skipped}, overwritten={self.overwritten})"
        )


def clone_profile(
    store_path: str,
    source: str,
    destination: str,
    passphrase: str,
    overwrite: bool = False,
    prefix: Optional[str] = None,
) -> CloneResult:
    """Clone all variables from source profile into destination profile.

    Args:
        store_path: Path to the envchain store directory.
        source: Name of the source profile.
        destination: Name of the destination profile.
        passphrase: Encryption passphrase.
        overwrite: If True, overwrite existing keys in destination.
        prefix: Optional prefix filter — only clone keys starting with this prefix.

    Returns:
        CloneResult with counts of copied/skipped/overwritten keys.
    """
    keys = list_profile_keys(store_path, source)
    if prefix:
        keys = [k for k in keys if k.startswith(prefix)]

    copied = skipped = overwritten = 0

    for key in keys:
        value = get_profile_variable(store_path, source, key, passphrase)
        if value is None:
            skipped += 1
            continue

        existing = get_profile_variable(store_path, destination, key, passphrase)
        if existing is not None and not overwrite:
            skipped += 1
            continue

        if existing is not None:
            overwritten += 1
        else:
            copied += 1

        set_profile_variable(store_path, destination, key, value, passphrase)

    return CloneResult(
        source=source,
        destination=destination,
        copied=copied,
        skipped=skipped,
        overwritten=overwritten,
    )
