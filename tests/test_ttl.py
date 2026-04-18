"""Tests for envchain.ttl module."""
import time
import pytest
from pathlib import Path
from envchain.ttl import set_ttl, clear_ttl, get_expiry, is_expired, purge_expired


@pytest.fixture
def store(tmp_path):
    return tmp_path / "test.env.json"


def test_set_and_get_expiry(store):
    set_ttl(store, "FOO", 60)
    expiry = get_expiry(store, "FOO")
    assert expiry is not None
    assert expiry > time.time()
    assert expiry <= time.time() + 61


def test_get_expiry_missing_key(store):
    assert get_expiry(store, "MISSING") is None


def test_is_expired_future(store):
    set_ttl(store, "FOO", 100)
    assert not is_expired(store, "FOO")


def test_is_expired_past(store):
    set_ttl(store, "FOO", -1)
    assert is_expired(store, "FOO")


def test_is_expired_no_ttl(store):
    assert not is_expired(store, "NO_TTL")


def test_clear_ttl(store):
    set_ttl(store, "FOO", 60)
    clear_ttl(store, "FOO")
    assert get_expiry(store, "FOO") is None


def test_clear_ttl_nonexistent(store):
    clear_ttl(store, "GHOST")  # should not raise


def test_purge_expired_removes_only_expired(store):
    set_ttl(store, "OLD", -1)
    set_ttl(store, "NEW", 100)
    expired = purge_expired(store)
    assert "OLD" in expired
    assert "NEW" not in expired
    assert get_expiry(store, "OLD") is None
    assert get_expiry(store, "NEW") is not None


def test_purge_expired_empty(store):
    assert purge_expired(store) == []


def test_multiple_keys(store):
    set_ttl(store, "A", 10)
    set_ttl(store, "B", 20)
    assert get_expiry(store, "A") < get_expiry(store, "B")
