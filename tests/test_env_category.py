"""Tests for envchain.env_category."""
import pytest
from pathlib import Path
from envchain.env_category import (
    set_category, get_category, remove_category,
    list_by_category, list_categories
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_set_and_get_category(store):
    result = set_category(store, "DB_URL", "database")
    assert result.success
    assert get_category(store, "DB_URL") == "database"


def test_get_missing_category_returns_none(store):
    assert get_category(store, "MISSING") is None


def test_overwrite_category(store):
    set_category(store, "API_KEY", "auth")
    set_category(store, "API_KEY", "secrets")
    assert get_category(store, "API_KEY") == "secrets"


def test_remove_category_returns_true(store):
    set_category(store, "TOKEN", "auth")
    assert remove_category(store, "TOKEN") is True
    assert get_category(store, "TOKEN") is None


def test_remove_missing_category_returns_false(store):
    assert remove_category(store, "NONEXISTENT") is False


def test_list_categories_empty(store):
    assert list_categories(store) == []


def test_list_categories_multiple(store):
    set_category(store, "DB_URL", "database")
    set_category(store, "API_KEY", "auth")
    set_category(store, "DB_PASS", "database")
    cats = list_categories(store)
    assert cats == ["auth", "database"]


def test_list_by_category_groups_correctly(store):
    set_category(store, "DB_URL", "database")
    set_category(store, "DB_PASS", "database")
    set_category(store, "API_KEY", "auth")
    grouped = list_by_category(store)
    assert set(grouped["database"]) == {"DB_URL", "DB_PASS"}
    assert grouped["auth"] == ["API_KEY"]


def test_set_empty_key_fails(store):
    result = set_category(store, "", "auth")
    assert not result.success
    assert "empty" in result.message.lower()


def test_set_empty_category_fails(store):
    result = set_category(store, "KEY", "")
    assert not result.success
