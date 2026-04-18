"""Search/filter environment variables across profiles and the default store."""

from __future__ import annotations

import fnmatch
from typing import List, Tuple

from envchain.store import list_keys, get_variable
from envchain.profile import list_profiles, get_profile_variable, list_profile_keys


def search_default(pattern: str, passphrase: str, store_path: str) -> List[Tuple[str, str]]:
    """Return (key, value) pairs from the default store matching *pattern*."""
    results = []
    for key in list_keys(store_path, passphrase):
        if fnmatch.fnmatch(key, pattern):
            value = get_variable(store_path, key, passphrase)
            results.append((key, value))
    return results


def search_profile(pattern: str, passphrase: str, store_path: str, profile: str) -> List[Tuple[str, str]]:
    """Return (key, value) pairs from *profile* matching *pattern*."""
    results = []
    for key in list_profile_keys(store_path, profile, passphrase):
        if fnmatch.fnmatch(key, pattern):
            value = get_profile_variable(store_path, profile, key, passphrase)
            results.append((key, value))
    return results


def search_all_profiles(pattern: str, passphrase: str, store_path: str) -> dict[str, List[Tuple[str, str]]]:
    """Search across all profiles and the default store.

    Returns a dict mapping profile name (or 'default') to matched (key, value) pairs.
    """
    results: dict[str, List[Tuple[str, str]]] = {}

    default_hits = search_default(pattern, passphrase, store_path)
    if default_hits:
        results["default"] = default_hits

    for profile in list_profiles(store_path):
        if profile == "default":
            continue
        hits = search_profile(pattern, passphrase, store_path, profile)
        if hits:
            results[profile] = hits

    return results


def search_keys_only(pattern: str, passphrase: str, store_path: str) -> dict[str, List[str]]:
    """Search for matching keys across all profiles and the default store, without decrypting values.

    Returns a dict mapping profile name (or 'default') to matched key names.
    This is faster than search_all_profiles when values are not needed.
    """
    results: dict[str, List[str]] = {}

    default_keys = [k for k in list_keys(store_path, passphrase) if fnmatch.fnmatch(k, pattern)]
    if default_keys:
        results["default"] = default_keys

    for profile in list_profiles(store_path):
        if profile == "default":
            continue
        matched = [k for k in list_profile_keys(store_path, profile, passphrase) if fnmatch.fnmatch(k, pattern)]
        if matched:
            results[profile] = matched

    return results
