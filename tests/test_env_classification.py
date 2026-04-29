"""Tests for envchain.env_classification."""

from __future__ import annotations

import pytest

from envchain.env_classification import (
    ClassificationResult,
    get_classification,
    list_classifications,
    remove_classification,
    set_classification,
)


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_classification(store):
    result = set_classification(store, "API_KEY", "secret")
    assert result.ok is True
    assert result.level == "secret"
    assert get_classification(store, "API_KEY") == "secret"


def test_get_missing_classification_returns_none(store):
    assert get_classification(store, "MISSING") is None


def test_invalid_level_returns_error(store):
    result = set_classification(store, "API_KEY", "top-secret")
    assert result.ok is False
    assert "Invalid level" in result.message


def test_overwrite_classification(store):
    set_classification(store, "DB_PASS", "confidential")
    set_classification(store, "DB_PASS", "secret")
    assert get_classification(store, "DB_PASS") == "secret"


def test_remove_classification_returns_true(store):
    set_classification(store, "TOKEN", "internal")
    assert remove_classification(store, "TOKEN") is True
    assert get_classification(store, "TOKEN") is None


def test_remove_missing_returns_false(store):
    assert remove_classification(store, "GHOST") is False


def test_list_classifications_empty(store):
    assert list_classifications(store) == {}


def test_list_classifications_multiple(store):
    set_classification(store, "A", "public")
    set_classification(store, "B", "secret")
    data = list_classifications(store)
    assert data == {"A": "public", "B": "secret"}


def test_classification_result_repr(store):
    result = set_classification(store, "X", "internal")
    assert "ClassificationResult" in repr(result)
    assert "internal" in repr(result)


def test_all_valid_levels_accepted(store):
    for level in ("public", "internal", "confidential", "secret"):
        r = set_classification(store, f"KEY_{level.upper()}", level)
        assert r.ok is True
