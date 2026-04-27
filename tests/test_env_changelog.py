"""Tests for envchain.env_changelog."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_changelog import (
    add_changelog_entry,
    get_changelog_entries,
    clear_changelog,
    list_keys_with_changelog,
    ChangelogEntry,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_add_changelog_returns_entry(store):
    entry = add_changelog_entry(store, "API_KEY", "Initial value set")
    assert isinstance(entry, ChangelogEntry)
    assert entry.key == "API_KEY"
    assert entry.message == "Initial value set"
    assert entry.author is None
    assert entry.timestamp


def test_add_changelog_with_author(store):
    entry = add_changelog_entry(store, "DB_PASS", "Rotated secret", author="alice")
    assert entry.author == "alice"


def test_get_changelog_returns_all_entries(store):
    add_changelog_entry(store, "TOKEN", "First entry")
    add_changelog_entry(store, "TOKEN", "Second entry")
    entries = get_changelog_entries(store, "TOKEN")
    assert len(entries) == 2
    assert entries[0].message == "First entry"
    assert entries[1].message == "Second entry"


def test_get_changelog_missing_key_returns_empty(store):
    entries = get_changelog_entries(store, "NONEXISTENT")
    assert entries == []


def test_clear_changelog_removes_entries(store):
    add_changelog_entry(store, "SECRET", "some change")
    result = clear_changelog(store, "SECRET")
    assert result is True
    assert get_changelog_entries(store, "SECRET") == []


def test_clear_changelog_missing_key_returns_false(store):
    result = clear_changelog(store, "MISSING")
    assert result is False


def test_list_keys_with_changelog(store):
    add_changelog_entry(store, "KEY_A", "msg a")
    add_changelog_entry(store, "KEY_B", "msg b")
    keys = list_keys_with_changelog(store)
    assert set(keys) == {"KEY_A", "KEY_B"}


def test_list_keys_empty_store(store):
    assert list_keys_with_changelog(store) == []


def test_add_empty_key_raises(store):
    with pytest.raises(ValueError, match="key"):
        add_changelog_entry(store, "", "some message")


def test_add_empty_message_raises(store):
    with pytest.raises(ValueError, match="message"):
        add_changelog_entry(store, "MY_KEY", "  ")


def test_repr_includes_key_and_message(store):
    entry = add_changelog_entry(store, "API_KEY", "Updated token", author="bob")
    text = repr(entry)
    assert "API_KEY" in text
    assert "Updated token" in text
    assert "bob" in text
