"""Merge variables from multiple profiles into one target profile."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from envchain.profile import list_profiles, get_profile_variable, set_profile_variable, list_profile_keys


@dataclass
class MergeResult:
    key: str
    source_profile: str
    target_profile: str
    status: str  # 'copied', 'skipped', 'overwritten'

    def __repr__(self) -> str:
        return f"MergeResult({self.key!r}, {self.source_profile!r}->{self.target_profile!r}, {self.status})"


def merge_profiles(
    store_path: str,
    sources: list[str],
    target: str,
    passphrase: str,
    overwrite: bool = False,
    keys: Optional[list[str]] = None,
) -> list[MergeResult]:
    """Merge variables from multiple source profiles into target profile.
    Sources are processed in order; later sources win when overwrite=True."""
    results: list[MergeResult] = []
    for source in sources:
        src_keys = list_profile_keys(store_path, source)
        if keys is not None:
            src_keys = [k for k in src_keys if k in keys]
        for key in src_keys:
            existing = get_profile_variable(store_path, target, key, passphrase)
            if existing is not None and not overwrite:
                results.append(MergeResult(key, source, target, "skipped"))
                continue
            value = get_profile_variable(store_path, source, key, passphrase)
            if value is None:
                continue
            set_profile_variable(store_path, target, key, value, passphrase)
            status = "overwritten" if existing is not None else "copied"
            results.append(MergeResult(key, source, target, status))
    return results


def merge_summary(results: list[MergeResult]) -> dict[str, int]:
    summary: dict[str, int] = {"copied": 0, "skipped": 0, "overwritten": 0}
    for r in results:
        summary[r.status] = summary.get(r.status, 0) + 1
    return summary
