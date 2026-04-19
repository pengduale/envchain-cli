"""Tests for envchain.env_priority."""

import pytest
from pathlib import Path

from envchain.store import set_variable
from envchain.profile import set_profile_variable
from envchain.env_priority import (
    set_priority,
    get_priority,
    remove_priority,
    resolve_variable,
)


@pytest.fixture
def store(tmp_path):
    store_path = tmp_path / "envchain.enc"
    return store_path


PASS = "testpass"


def test_set_and_get_priority(store):
    set_priority(store, "API_KEY", ["staging", "default"])
    assert get_priority(store, "API_KEY") == ["staging", "default"]


def test_get_priority_missing_returns_none(store):
    assert get_priority(store, "MISSING") is None


def test_set_priority_empty_list_raises(store):
    with pytest.raises(ValueError):
        set_priority(store, "KEY", [])


def test_remove_priority_returns_true(store):
    set_priority(store, "DB_URL", ["prod", "default"])
    assert remove_priority(store, "DB_URL") is True
    assert get_priority(store, "DB_URL") is None


def test_remove_priority_missing_returns_false(store):
    assert remove_priority(store, "NOPE") is False


def test_resolve_variable_from_default(store):
    set_variable(store, "TOKEN", "abc123", PASS)
    result = resolve_variable(store, "TOKEN", PASS)
    assert result.value == "abc123"
    assert result.resolved_from == "default"
    assert "default" in result.tried


def test_resolve_variable_prefers_first_profile(store):
    set_variable(store, "TOKEN", "default_val", PASS)
    set_profile_variable(store, "staging", "TOKEN", "staging_val", PASS)
    set_priority(store, "TOKEN", ["staging", "default"])
    result = resolve_variable(store, "TOKEN", PASS)
    assert result.value == "staging_val"
    assert result.resolved_from == "staging"


def test_resolve_variable_falls_back_to_next(store):
    set_variable(store, "TOKEN", "default_val", PASS)
    set_priority(store, "TOKEN", ["staging", "default"])
    # staging does not have TOKEN, should fall back to default
    result = resolve_variable(store, "TOKEN", PASS)
    assert result.value == "default_val"
    assert result.resolved_from == "default"
    assert "staging" in result.tried


def test_resolve_variable_not_found_anywhere(store):
    set_priority(store, "GHOST", ["staging", "default"])
    result = resolve_variable(store, "GHOST", PASS)
    assert result.value is None
    assert result.resolved_from is None
