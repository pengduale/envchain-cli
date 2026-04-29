"""Tests for envchain.env_signature."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envchain.env_signature import (
    list_signatures,
    remove_signature,
    sign_variable,
    verify_variable,
)

SECRET = "test-secret-key"


@pytest.fixture()
def store(tmp_path):
    store_file = tmp_path / "store.json"
    store_file.write_text("{}")
    return store_file


def test_sign_returns_ok(store):
    result = sign_variable(store, "MY_KEY", "my_value", SECRET)
    assert result.ok is True
    assert result.key == "MY_KEY"
    assert len(result.digest) == 64  # sha256 hex
    assert result.signed_at > 0


def test_sign_creates_file(store):
    sign_variable(store, "MY_KEY", "v1", SECRET)
    sig_file = store.parent / "signatures.json"
    assert sig_file.exists()
    data = json.loads(sig_file.read_text())
    assert "MY_KEY" in data


def test_sign_empty_key_returns_error(store):
    result = sign_variable(store, "", "value", SECRET)
    assert result.ok is False
    assert result.error == "empty key"


def test_verify_correct_value_passes(store):
    sign_variable(store, "DB_PASS", "secret123", SECRET)
    result = verify_variable(store, "DB_PASS", "secret123", SECRET)
    assert result.ok is True
    assert result.error is None


def test_verify_wrong_value_fails(store):
    sign_variable(store, "DB_PASS", "secret123", SECRET)
    result = verify_variable(store, "DB_PASS", "wrong_value", SECRET)
    assert result.ok is False
    assert result.error == "digest mismatch"


def test_verify_wrong_secret_fails(store):
    sign_variable(store, "API_KEY", "abc", SECRET)
    result = verify_variable(store, "API_KEY", "abc", "other-secret")
    assert result.ok is False


def test_verify_missing_key_returns_error(store):
    result = verify_variable(store, "MISSING", "value", SECRET)
    assert result.ok is False
    assert result.error == "no signature"


def test_remove_existing_signature(store):
    sign_variable(store, "TOKEN", "val", SECRET)
    removed = remove_signature(store, "TOKEN")
    assert removed is True
    result = verify_variable(store, "TOKEN", "val", SECRET)
    assert result.ok is False
    assert result.error == "no signature"


def test_remove_missing_returns_false(store):
    assert remove_signature(store, "GHOST") is False


def test_list_signatures_empty(store):
    assert list_signatures(store) == []


def test_list_signatures_returns_all(store):
    sign_variable(store, "A", "1", SECRET)
    sign_variable(store, "B", "2", SECRET)
    entries = list_signatures(store)
    keys = {e["key"] for e in entries}
    assert keys == {"A", "B"}


def test_overwrite_signature_updates_digest(store):
    sign_variable(store, "K", "old", SECRET)
    r1 = sign_variable(store, "K", "new", SECRET)
    r2 = verify_variable(store, "K", "new", SECRET)
    assert r2.ok is True
    assert r1.digest == r2.digest
