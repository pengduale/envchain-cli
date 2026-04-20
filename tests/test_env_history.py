"""Tests for envchain.env_history."""
from __future__ import annotations

import time
import pytest
from pathlib import Path

from envchain.env_history import (
    record_event,
    get_history,
    clear_history,
    list_keys_with_history,
    HistoryEntry,
)


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    p = tmp_path / "envchain.enc"
    p.write_text("{}")
    return p


def test_record_event_returns_history_entry(store):
    entry = record_event(store, "API_KEY", "set", value="secret123")
    assert isinstance(entry, HistoryEntry)
    assert entry.key == "API_KEY"
    assert entry.action == "set"


def test_preview_masks_value(store):
    entry = record_event(store, "TOKEN", "set", value="abcdefgh")
    assert entry.preview == "abcd****"


def test_preview_short_value_fully_masked(store):
    entry = record_event(store, "X", "set", value="ab")
    assert entry.preview == "****"


def test_delete_action_no_preview(store):
    entry = record_event(store, "API_KEY", "delete")
    assert entry.action == "delete"
    assert entry.preview is None


def test_invalid_action_raises(store):
    with pytest.raises(ValueError, match="Invalid action"):
        record_event(store, "KEY", "update")


def test_get_history_empty(store):
    assert get_history(store, "MISSING") == []


def test_get_history_returns_entries_in_order(store):
    record_event(store, "DB_PASS", "set", value="first")
    time.sleep(0.01)
    record_event(store, "DB_PASS", "set", value="second")
    entries = get_history(store, "DB_PASS")
    assert len(entries) == 2
    assert entries[0].timestamp <= entries[1].timestamp


def test_list_keys_with_history(store):
    record_event(store, "A", "set", value="1")
    record_event(store, "B", "set", value="2")
    keys = list_keys_with_history(store)
    assert "A" in keys
    assert "B" in keys


def test_clear_history_single_key(store):
    record_event(store, "A", "set", value="1")
    record_event(store, "B", "set", value="2")
    removed = clear_history(store, key="A")
    assert removed == 1
    assert get_history(store, "A") == []
    assert len(get_history(store, "B")) == 1


def test_clear_history_all_keys(store):
    record_event(store, "A", "set", value="1")
    record_event(store, "A", "set", value="2")
    record_event(store, "B", "set", value="3")
    removed = clear_history(store)
    assert removed == 3
    assert list_keys_with_history(store) == []


def test_max_per_key_truncates_old_entries(store):
    for i in range(10):
        record_event(store, "K", "set", value=str(i), max_per_key=5)
    entries = get_history(store, "K")
    assert len(entries) == 5
    # newest 5 values should be 5..9
    previews = [e.preview for e in entries]
    assert all(p is not None for p in previews)
