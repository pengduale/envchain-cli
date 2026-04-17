"""Tests for envchain.store."""

import json
import pytest
from pathlib import Path

from envchain.store import set_variable, get_variable, delete_variable, list_keys

PASS = "test-passphrase"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / ".envchain"


def test_set_creates_file(store):
    set_variable("FOO", "bar", PASS, store)
    assert store.exists()


def test_set_and_get_roundtrip(store):
    set_variable("DB_URL", "postgres://localhost/db", PASS, store)
    assert get_variable("DB_URL", PASS, store) == "postgres://localhost/db"


def test_multiple_keys(store):
    set_variable("KEY_A", "alpha", PASS, store)
    set_variable("KEY_B", "beta", PASS, store)
    assert get_variable("KEY_A", PASS, store) == "alpha"
    assert get_variable("KEY_B", PASS, store) == "beta"


def test_list_keys(store):
    set_variable("Z", "1", PASS, store)
    set_variable("A", "2", PASS, store)
    assert list_keys(store) == ["A", "Z"]


def test_delete_variable(store):
    set_variable("TO_DEL", "val", PASS, store)
    delete_variable("TO_DEL", store)
    assert "TO_DEL" not in list_keys(store)


def test_delete_missing_raises(store):
    with pytest.raises(KeyError):
        delete_variable("GHOST", store)


def test_get_missing_raises(store):
    with pytest.raises(KeyError):
        get_variable("MISSING", PASS, store)


def test_store_file_is_valid_json(store):
    set_variable("X", "y", PASS, store)
    data = json.loads(store.read_text())
    assert "X" in data
