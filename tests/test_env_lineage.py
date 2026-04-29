"""Tests for envchain.env_lineage."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envchain.env_lineage import (
    record_lineage,
    get_lineage,
    clear_lineage,
    list_lineage_keys,
    LineageEntry,
)


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_record_lineage_returns_entry(store):
    entry = record_lineage(store, "API_KEY", "API_KEY", "default", "copy")
    assert isinstance(entry, LineageEntry)
    assert entry.key == "API_KEY"
    assert entry.source_key == "API_KEY"
    assert entry.source_profile == "default"
    assert entry.operation == "copy"
    assert entry.note is None


def test_record_lineage_with_note(store):
    entry = record_lineage(store, "DB_PASS", "DB_PASS", "staging", "promote", note="promoted to prod")
    assert entry.note == "promoted to prod"


def test_record_lineage_creates_file(store):
    record_lineage(store, "TOKEN", "TOKEN", "dev", "clone")
    assert (store / ".lineage.json").exists()


def test_get_lineage_returns_all_entries(store):
    record_lineage(store, "KEY", "KEY", "dev", "copy")
    record_lineage(store, "KEY", "KEY", "staging", "promote")
    entries = get_lineage(store, "KEY")
    assert len(entries) == 2
    assert entries[0].source_profile == "dev"
    assert entries[1].source_profile == "staging"


def test_get_lineage_missing_key_returns_empty(store):
    result = get_lineage(store, "MISSING")
    assert result == []


def test_record_lineage_invalid_operation_raises(store):
    with pytest.raises(ValueError, match="Invalid operation"):
        record_lineage(store, "X", "X", "default", "teleport")


def test_clear_lineage_removes_key(store):
    record_lineage(store, "SECRET", "SECRET", "prod", "manual")
    removed = clear_lineage(store, "SECRET")
    assert removed is True
    assert get_lineage(store, "SECRET") == []


def test_clear_lineage_missing_key_returns_false(store):
    result = clear_lineage(store, "NONEXISTENT")
    assert result is False


def test_list_lineage_keys_empty(store):
    assert list_lineage_keys(store) == []


def test_list_lineage_keys_multiple(store):
    record_lineage(store, "A", "A", "dev", "copy")
    record_lineage(store, "B", "B", "prod", "import")
    keys = list_lineage_keys(store)
    assert set(keys) == {"A", "B"}


def test_entry_timestamp_is_recent(store):
    before = time.time()
    entry = record_lineage(store, "T", "T", "default", "merge")
    after = time.time()
    assert before <= entry.timestamp <= after


def test_lineage_entry_repr(store):
    entry = record_lineage(store, "FOO", "BAR", "staging", "clone")
    r = repr(entry)
    assert "FOO" in r
    assert "clone" in r
