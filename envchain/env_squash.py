"""Squash multiple profiles into one by merging all keys."""
from dataclasses import dataclass
from typing import List, Optional
from envchain.profile import list_profiles, get_profile_variable, set_profile_variable


@dataclass
class SquashResult:
    key: str
    source_profile: str
    written: bool
    reason: Optional[str] = None

    def __repr__(self):
        return f"SquashResult(key={self.key!r}, source={self.source_profile!r}, written={self.written})"


def squash_profiles(
    store_path,
    passphrase: str,
    profiles: List[str],
    dest: str = "default",
    overwrite: bool = False,
) -> List[SquashResult]:
    results = []
    seen_keys = set()
    for profile in profiles:
        all_profiles = list_profiles(store_path)
        if profile not in all_profiles:
            continue
        from envchain.profile import list_profile_keys
        keys = list_profile_keys(store_path, profile)
        for key in keys:
            if key in seen_keys and not overwrite:
                results.append(SquashResult(key=key, source_profile=profile, written=False, reason="already written from earlier profile"))
                continue
            value = get_profile_variable(store_path, passphrase, profile, key)
            if value is None:
                results.append(SquashResult(key=key, source_profile=profile, written=False, reason="read error"))
                continue
            existing = get_profile_variable(store_path, passphrase, dest, key)
            if existing is not None and not overwrite:
                results.append(SquashResult(key=key, source_profile=profile, written=False, reason="exists in dest"))
                continue
            set_profile_variable(store_path, passphrase, dest, key, value)
            seen_keys.add(key)
            results.append(SquashResult(key=key, source_profile=profile, written=True))
    return results
