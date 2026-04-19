"""env_status.py – summarise the health/status of a store at a glance."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envchain.store import list_keys, get_variable
from envchain.ttl import is_expired, get_expiry
from envchain.tags import get_tags
from envchain.env_mask import is_masked


@dataclass
class KeyStatus:
    key: str
    has_value: bool
    expired: bool
    tags: List[str] = field(default_factory=list)
    masked: bool = False

    def __repr__(self) -> str:  # pragma: no cover
        flags = []
        if self.expired:
            flags.append("EXPIRED")
        if self.masked:
            flags.append("MASKED")
        tag_str = ",".join(self.tags) if self.tags else "-"
        flag_str = ",".join(flags) if flags else "ok"
        return f"<KeyStatus {self.key} tags=[{tag_str}] {flag_str}>"


@dataclass
class StoreStatus:
    total: int
    expired: int
    masked: int
    keys: List[KeyStatus] = field(default_factory=list)


def status_for_store(store_path: Path, passphrase: str) -> StoreStatus:
    """Return a StoreStatus describing every key in the store."""
    keys = list_keys(store_path)
    key_statuses: List[KeyStatus] = []
    for k in keys:
        try:
            val = get_variable(store_path, k, passphrase)
            has_value = val is not None
        except Exception:
            has_value = False
        expired = is_expired(store_path, k)
        tags = get_tags(store_path, k)
        masked = is_masked(store_path, k)
        key_statuses.append(KeyStatus(key=k, has_value=has_value, expired=expired, tags=tags, masked=masked))

    return StoreStatus(
        total=len(key_statuses),
        expired=sum(1 for s in key_statuses if s.expired),
        masked=sum(1 for s in key_statuses if s.masked),
        keys=key_statuses,
    )
