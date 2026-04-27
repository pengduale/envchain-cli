"""Expiry reminder: compute upcoming and overdue expirations for stored keys."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envchain.ttl import _load_ttl


@dataclass
class ReminderEntry:
    key: str
    expires_at: datetime.datetime
    days_remaining: float
    overdue: bool

    def __repr__(self) -> str:  # pragma: no cover
        status = "OVERDUE" if self.overdue else f"{self.days_remaining:.1f}d remaining"
        return f"<ReminderEntry key={self.key!r} expires_at={self.expires_at.isoformat()} {status}>"


def get_expiry_reminders(
    store_path: Path,
    warn_within_days: int = 7,
    include_overdue: bool = True,
) -> List[ReminderEntry]:
    """Return keys expiring within *warn_within_days* days (and optionally overdue ones)."""
    ttl_data = _load_ttl(store_path)
    now = datetime.datetime.utcnow()
    cutoff = now + datetime.timedelta(days=warn_within_days)
    results: List[ReminderEntry] = []

    for key, iso_ts in ttl_data.items():
        try:
            expires_at = datetime.datetime.fromisoformat(iso_ts)
        except ValueError:
            continue

        overdue = expires_at < now
        days_remaining = (expires_at - now).total_seconds() / 86400.0

        if overdue and include_overdue:
            results.append(ReminderEntry(key=key, expires_at=expires_at,
                                         days_remaining=days_remaining, overdue=True))
        elif not overdue and expires_at <= cutoff:
            results.append(ReminderEntry(key=key, expires_at=expires_at,
                                         days_remaining=days_remaining, overdue=False))

    results.sort(key=lambda e: e.expires_at)
    return results


def summary(reminders: List[ReminderEntry]) -> str:
    """Return a human-readable summary line."""
    overdue = sum(1 for r in reminders if r.overdue)
    upcoming = len(reminders) - overdue
    return f"{overdue} overdue, {upcoming} expiring soon"
