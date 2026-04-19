"""Tests for envchain.env_label."""

import pytest
from pathlib import Path
from envchain.env_label import (
    set_label,
    get_label,
    remove_label,
    list_labels,
    search_labels,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_label(store):
    set_label(store, "API_KEY", "Primary API key for external service")
    assert get_label(store, "API_KEY") == "Primary API key for external service"


def test_get_missing_label_returns_none(store):
    assert get_label(store, "MISSING") is None


def test_overwrite_label(store):
    set_label(store, "DB_PASS", "old description")
    set_label(store, "DB_PASS", "new description")
    assert get_label(store, "DB_PASS") == "new description"


def test_remove_label_returns_true(store):
    set_label(store, "TOKEN", "some token")
    assert remove_label(store, "TOKEN") is True
    assert get_label(store, "TOKEN") is None


def test_remove_missing_label_returns_false(store):
    assert remove_label(store, "GHOST") is False


def test_list_labels_empty(store):
    assert list_labels(store) == {}


def test_list_labels_multiple(store):
    set_label(store, "A", "alpha")
    set_label(store, "B", "beta")
    result = list_labels(store)
    assert result == {"A": "alpha", "B": "beta"}


def test_search_labels_finds_match(store):
    set_label(store, "AWS_KEY", "Amazon Web Services key")
    set_label(store, "GH_TOKEN", "GitHub personal token")
    result = search_labels(store, "amazon")
    assert "AWS_KEY" in result
    assert "GH_TOKEN" not in result


def test_search_labels_case_insensitive(store):
    set_label(store, "X", "My Secret Value")
    assert "X" in search_labels(store, "secret")
    assert "X" in search_labels(store, "SECRET")


def test_search_labels_no_match(store):
    set_label(store, "Y", "something else")
    assert search_labels(store, "zzz") == {}
