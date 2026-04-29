"""Tests for envchain.env_access_log."""

import pytest
from pathlib import Path

from envchain.env_access_log import (
    record_access,
    get_access_log,
    clear_access_log,
    all_accessed_keys,
    AccessEntry,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_record_access_returns_entry(store):
    entry = record_access(store, "DB_URL", "read")
    assert isinstance(entry, AccessEntry)
    assert entry.key == "DB_URL"
    assert entry.action == "read"
    assert entry.timestamp
    assert entry.actor is None


def test_record_access_with_actor(store):
    entry = record_access(store, "API_KEY", "write", actor="alice")
    assert entry.actor == "alice"


def test_record_access_invalid_action_raises(store):
    with pytest.raises(ValueError, match="Invalid action"):
        record_access(store, "KEY", "update")


def test_record_access_empty_key_raises(store):
    with pytest.raises(ValueError, match="empty"):
        record_access(store, "", "read")


def test_get_access_log_empty(store):
    result = get_access_log(store, "MISSING_KEY")
    assert result == []


def test_get_access_log_returns_entries(store):
    record_access(store, "SECRET", "write")
    record_access(store, "SECRET", "read")
    entries = get_access_log(store, "SECRET")
    assert len(entries) == 2
    assert entries[0].action == "write"
    assert entries[1].action == "read"


def test_multiple_keys_are_independent(store):
    record_access(store, "KEY_A", "read")
    record_access(store, "KEY_B", "delete")
    assert len(get_access_log(store, "KEY_A")) == 1
    assert len(get_access_log(store, "KEY_B")) == 1
    assert get_access_log(store, "KEY_A")[0].action == "read"


def test_all_accessed_keys(store):
    record_access(store, "X", "read")
    record_access(store, "Y", "write")
    keys = all_accessed_keys(store)
    assert set(keys) == {"X", "Y"}


def test_clear_access_log_returns_true(store):
    record_access(store, "TOKEN", "read")
    result = clear_access_log(store, "TOKEN")
    assert result is True
    assert get_access_log(store, "TOKEN") == []


def test_clear_access_log_missing_key_returns_false(store):
    result = clear_access_log(store, "NONEXISTENT")
    assert result is False


def test_access_entry_repr(store):
    entry = record_access(store, "DB_PASS", "delete", actor="bob")
    r = repr(entry)
    assert "delete" in r
    assert "DB_PASS" in r
    assert "bob" in r
