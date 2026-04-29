"""Tests for envchain.env_attestation."""
from __future__ import annotations

import time
import pytest
from pathlib import Path

from envchain.env_attestation import (
    attest_variable,
    get_attestation,
    remove_attestation,
    list_attestations,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_attest_variable_returns_ok(store):
    result = attest_variable(store, "API_KEY", "alice")
    assert result.ok is True
    assert result.key == "API_KEY"
    assert result.attested_by == "alice"
    assert result.error is None


def test_attest_variable_stores_timestamp(store):
    before = time.time()
    result = attest_variable(store, "DB_PASS", "bob")
    after = time.time()
    assert before <= result.attested_at <= after


def test_attest_variable_with_note(store):
    result = attest_variable(store, "SECRET", "carol", note="verified in sprint 42")
    assert result.note == "verified in sprint 42"


def test_get_attestation_after_set(store):
    attest_variable(store, "TOKEN", "dave")
    r = get_attestation(store, "TOKEN")
    assert r is not None
    assert r.attested_by == "dave"
    assert r.ok is True


def test_get_missing_attestation_returns_none(store):
    assert get_attestation(store, "NONEXISTENT") is None


def test_attest_empty_key_returns_error(store):
    result = attest_variable(store, "", "eve")
    assert result.ok is False
    assert "empty" in result.error


def test_attest_empty_attested_by_returns_error(store):
    result = attest_variable(store, "KEY", "")
    assert result.ok is False
    assert "attested_by" in result.error


def test_overwrite_attestation(store):
    attest_variable(store, "KEY", "alice")
    attest_variable(store, "KEY", "bob", note="re-attested")
    r = get_attestation(store, "KEY")
    assert r.attested_by == "bob"
    assert r.note == "re-attested"


def test_remove_attestation_returns_true(store):
    attest_variable(store, "KEY", "alice")
    assert remove_attestation(store, "KEY") is True
    assert get_attestation(store, "KEY") is None


def test_remove_missing_attestation_returns_false(store):
    assert remove_attestation(store, "MISSING") is False


def test_list_attestations_empty(store):
    assert list_attestations(store) == []


def test_list_attestations_multiple(store):
    attest_variable(store, "A", "alice")
    attest_variable(store, "B", "bob")
    results = list_attestations(store)
    keys = {r.key for r in results}
    assert keys == {"A", "B"}
