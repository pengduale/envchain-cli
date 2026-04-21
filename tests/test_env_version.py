"""Tests for envchain.env_version module."""
import time
import pytest
from pathlib import Path

from envchain.env_version import (
    record_version,
    get_versions,
    get_latest_version,
    clear_versions,
    list_versioned_keys,
    VersionEntry,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "envchain.enc"
    store_file.write_text("{}")
    return store_file


def test_record_version_returns_entry(store):
    entry = record_version(store, "API_KEY", "supersecret")
    assert isinstance(entry, VersionEntry)
    assert entry.version == 1
    assert "****" in entry.preview


def test_record_version_increments(store):
    record_version(store, "API_KEY", "value1")
    entry2 = record_version(store, "API_KEY", "value2")
    assert entry2.version == 2


def test_get_versions_empty(store):
    result = get_versions(store, "MISSING_KEY")
    assert result == []


def test_get_versions_returns_all(store):
    record_version(store, "DB_PASS", "pass1")
    record_version(store, "DB_PASS", "pass2")
    record_version(store, "DB_PASS", "pass3")
    versions = get_versions(store, "DB_PASS")
    assert len(versions) == 3
    assert [v.version for v in versions] == [1, 2, 3]


def test_get_latest_version_returns_last(store):
    record_version(store, "TOKEN", "old")
    record_version(store, "TOKEN", "new")
    latest = get_latest_version(store, "TOKEN")
    assert latest is not None
    assert latest.version == 2


def test_get_latest_version_missing_key(store):
    assert get_latest_version(store, "NONEXISTENT") is None


def test_preview_masks_short_value(store):
    entry = record_version(store, "X", "ab")
    assert entry.preview == "****"


def test_preview_shows_prefix_for_long_value(store):
    entry = record_version(store, "X", "abcdefgh")
    assert entry.preview.startswith("abcd")
    assert "****" in entry.preview


def test_clear_versions_removes_all(store):
    record_version(store, "KEY", "v1")
    record_version(store, "KEY", "v2")
    removed = clear_versions(store, "KEY")
    assert removed == 2
    assert get_versions(store, "KEY") == []


def test_clear_versions_missing_key_returns_zero(store):
    assert clear_versions(store, "GHOST") == 0


def test_list_versioned_keys(store):
    record_version(store, "A", "val")
    record_version(store, "B", "val")
    keys = list_versioned_keys(store)
    assert set(keys) == {"A", "B"}


def test_list_versioned_keys_empty_store(store):
    assert list_versioned_keys(store) == []


def test_versions_are_isolated_per_key(store):
    record_version(store, "K1", "x")
    record_version(store, "K2", "y")
    record_version(store, "K2", "z")
    assert len(get_versions(store, "K1")) == 1
    assert len(get_versions(store, "K2")) == 2


def test_timestamp_is_recent(store):
    before = time.time()
    entry = record_version(store, "TS_KEY", "value")
    after = time.time()
    assert before <= entry.timestamp <= after
