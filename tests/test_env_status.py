"""Tests for envchain.env_status."""
from __future__ import annotations
from pathlib import Path
import pytest

from envchain.store import set_variable
from envchain.ttl import set_ttl
from envchain.env_mask import mask_variable
from envchain.tags import tag_variable
from envchain.env_status import status_for_store, KeyStatus

PASS = "hunter2"


@pytest.fixture()
def store(tmp_path):
    return tmp_path / "store.json"


def test_empty_store_returns_zero_totals(store):
    store.write_text("{}")
    result = status_for_store(store, PASS)
    assert result.total == 0
    assert result.expired == 0
    assert result.masked == 0
    assert result.keys == []


def test_single_key_present(store):
    set_variable(store, "API_KEY", "secret", PASS)
    result = status_for_store(store, PASS)
    assert result.total == 1
    assert result.keys[0].key == "API_KEY"
    assert result.keys[0].has_value is True
    assert result.keys[0].expired is False


def test_expired_key_counted(store):
    import time
    set_variable(store, "OLD_KEY", "val", PASS)
    set_ttl(store, "OLD_KEY", int(time.time()) - 10)
    result = status_for_store(store, PASS)
    assert result.expired == 1
    assert result.keys[0].expired is True


def test_masked_key_counted(store):
    set_variable(store, "SECRET", "topsecret", PASS)
    mask_variable(store, "SECRET")
    result = status_for_store(store, PASS)
    assert result.masked == 1
    assert result.keys[0].masked is True


def test_tags_reported(store):
    set_variable(store, "DB_PASS", "dbsecret", PASS)
    tag_variable(store, "DB_PASS", "database")
    tag_variable(store, "DB_PASS", "prod")
    result = status_for_store(store, PASS)
    assert "database" in result.keys[0].tags
    assert "prod" in result.keys[0].tags


def test_multiple_keys_totals(store):
    for i in range(5):
        set_variable(store, f"KEY_{i}", f"val{i}", PASS)
    result = status_for_store(store, PASS)
    assert result.total == 5
