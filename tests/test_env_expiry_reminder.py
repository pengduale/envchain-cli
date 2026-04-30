"""Tests for env_expiry_reminder module."""

from __future__ import annotations

import datetime
import json
from pathlib import Path

import pytest

from envchain.env_expiry_reminder import get_expiry_reminders, summary, ReminderEntry
from envchain.ttl import _ttl_path


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    (tmp_path / ".envchain").mkdir()
    return tmp_path


def _write_ttl(store: Path, data: dict) -> None:
    path = _ttl_path(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def _future(days: float) -> str:
    dt = datetime.datetime.utcnow() + datetime.timedelta(days=days)
    return dt.isoformat()


def _past(days: float) -> str:
    dt = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    return dt.isoformat()


def test_no_ttl_returns_empty(store: Path):
    result = get_expiry_reminders(store)
    assert result == []


def test_key_expiring_soon_included(store: Path):
    _write_ttl(store, {"API_KEY": _future(3)})
    result = get_expiry_reminders(store, warn_within_days=7)
    assert len(result) == 1
    assert result[0].key == "API_KEY"
    assert not result[0].overdue
    assert 2.9 < result[0].days_remaining < 3.1


def test_key_far_future_excluded(store: Path):
    _write_ttl(store, {"API_KEY": _future(30)})
    result = get_expiry_reminders(store, warn_within_days=7)
    assert result == []


def test_overdue_key_included(store: Path):
    _write_ttl(store, {"OLD_KEY": _past(2)})
    result = get_expiry_reminders(store, include_overdue=True)
    assert len(result) == 1
    assert result[0].overdue is True
    assert result[0].days_remaining < 0


def test_overdue_key_excluded_when_flag_false(store: Path):
    _write_ttl(store, {"OLD_KEY": _past(2)})
    result = get_expiry_reminders(store, include_overdue=False)
    assert result == []


def test_results_sorted_by_expiry(store: Path):
    _write_ttl(store, {"B": _future(5), "A": _future(2), "C": _future(1)})
    result = get_expiry_reminders(store, warn_within_days=10)
    assert [r.key for r in result] == ["C", "A", "B"]


def test_invalid_timestamp_skipped(store: Path):
    _write_ttl(store, {"BAD": "not-a-date", "GOOD": _future(1)})
    result = get_expiry_reminders(store, warn_within_days=7)
    assert len(result) == 1
    assert result[0].key == "GOOD"


def test_summary_string(store: Path):
    reminders = [
        ReminderEntry("A", datetime.datetime.utcnow(), -1.0, overdue=True),
        ReminderEntry("B", datetime.datetime.utcnow(), 2.0, overdue=False),
        ReminderEntry("C", datetime.datetime.utcnow(), 5.0, overdue=False),
    ]
    assert summary(reminders) == "1 overdue, 2 expiring soon"


def test_summary_empty():
    assert summary([]) == "0 overdue, 0 expiring soon"


def test_summary_only_overdue():
    """summary() correctly reports when all entries are overdue and none are upcoming."""
    reminders = [
        ReminderEntry("X", datetime.datetime.utcnow(), -3.0, overdue=True),
        ReminderEntry("Y", datetime.datetime.utcnow(), -1.0, overdue=True),
    ]
    assert summary(reminders) == "2 overdue, 0 expiring soon"


def test_summary_only_expiring_soon():
    """summary() correctly reports when all entries are upcoming and none are overdue."""
    reminders = [
        ReminderEntry("M", datetime.datetime.utcnow(), 1.0, overdue=False),
        ReminderEntry("N", datetime.datetime.utcnow(), 4.0, overdue=False),
    ]
    assert summary(reminders) == "0 overdue, 2 expiring soon"
