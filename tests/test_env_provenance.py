"""Tests for envchain.env_provenance."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_provenance import (
    set_provenance,
    get_provenance,
    remove_provenance,
    list_provenance,
    VALID_ORIGINS,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return str(store_file)


def test_set_and_get_provenance(store):
    result = set_provenance(store, "DB_URL", "vault")
    assert result.ok
    assert result.key == "DB_URL"
    assert result.origin == "vault"

    fetched = get_provenance(store, "DB_URL")
    assert fetched is not None
    assert fetched.origin == "vault"
    assert fetched.key == "DB_URL"


def test_get_missing_provenance_returns_none(store):
    assert get_provenance(store, "MISSING_KEY") is None


def test_set_provenance_with_url_and_actor(store):
    result = set_provenance(
        store, "API_KEY", "ci",
        source_url="https://ci.example.com/job/42",
        recorded_by="deploy-bot",
        note="Injected during release pipeline",
    )
    assert result.ok
    fetched = get_provenance(store, "API_KEY")
    assert fetched.source_url == "https://ci.example.com/job/42"
    assert fetched.recorded_by == "deploy-bot"
    assert fetched.note == "Injected during release pipeline"


def test_overwrite_provenance(store):
    set_provenance(store, "TOKEN", "manual")
    set_provenance(store, "TOKEN", "generated")
    fetched = get_provenance(store, "TOKEN")
    assert fetched.origin == "generated"


def test_invalid_origin_returns_error(store):
    result = set_provenance(store, "KEY", "unknown-source")
    assert not result.ok
    assert "invalid origin" in result.error


def test_empty_key_returns_error(store):
    result = set_provenance(store, "", "manual")
    assert not result.ok
    assert "empty" in result.error


def test_remove_provenance_returns_true(store):
    set_provenance(store, "SECRET", "vault")
    assert remove_provenance(store, "SECRET") is True
    assert get_provenance(store, "SECRET") is None


def test_remove_missing_returns_false(store):
    assert remove_provenance(store, "NONEXISTENT") is False


def test_list_provenance_empty(store):
    assert list_provenance(store) == []


def test_list_provenance_multiple(store):
    set_provenance(store, "A", "manual")
    set_provenance(store, "B", "ci")
    set_provenance(store, "C", "vault")
    entries = list_provenance(store)
    keys = {e.key for e in entries}
    assert keys == {"A", "B", "C"}


def test_all_valid_origins_accepted(store):
    for i, origin in enumerate(VALID_ORIGINS):
        result = set_provenance(store, f"KEY_{i}", origin)
        assert result.ok, f"Expected origin '{origin}' to be valid"


def test_provenance_file_created(store):
    set_provenance(store, "X", "import")
    prov_file = Path(store).parent / "provenance.json"
    assert prov_file.exists()
