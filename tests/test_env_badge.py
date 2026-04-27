"""Tests for envchain.env_badge."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_badge import (
    add_badge,
    remove_badge,
    get_badges,
    list_all_badges,
    VALID_BADGES,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_add_badge_returns_ok(store):
    result = add_badge(store, "API_KEY", "stable")
    assert result.ok
    assert "stable" in result.badges


def test_add_badge_no_duplicates(store):
    add_badge(store, "API_KEY", "stable")
    result = add_badge(store, "API_KEY", "stable")
    assert result.badges.count("stable") == 1


def test_add_multiple_badges(store):
    add_badge(store, "DB_PASS", "critical")
    add_badge(store, "DB_PASS", "internal")
    badges = get_badges(store, "DB_PASS")
    assert "critical" in badges
    assert "internal" in badges


def test_add_invalid_badge_raises(store):
    with pytest.raises(ValueError, match="Invalid badge"):
        add_badge(store, "KEY", "unknown_badge")


def test_remove_badge_returns_ok(store):
    add_badge(store, "TOKEN", "deprecated")
    result = remove_badge(store, "TOKEN", "deprecated")
    assert result.ok
    assert "deprecated" not in result.badges


def test_remove_missing_badge_returns_not_ok(store):
    result = remove_badge(store, "TOKEN", "stable")
    assert not result.ok
    assert "not found" in result.message


def test_get_badges_returns_none_for_unknown_key(store):
    assert get_badges(store, "NONEXISTENT") is None


def test_get_badges_after_add(store):
    add_badge(store, "SECRET", "experimental")
    badges = get_badges(store, "SECRET")
    assert badges == ["experimental"]


def test_list_all_badges_empty(store):
    assert list_all_badges(store) == {}


def test_list_all_badges_multiple_keys(store):
    add_badge(store, "A", "stable")
    add_badge(store, "B", "deprecated")
    add_badge(store, "B", "internal")
    result = list_all_badges(store)
    assert set(result["A"]) == {"stable"}
    assert set(result["B"]) == {"deprecated", "internal"}


def test_valid_badges_set_is_nonempty():
    assert len(VALID_BADGES) > 0
    assert "stable" in VALID_BADGES
    assert "deprecated" in VALID_BADGES
