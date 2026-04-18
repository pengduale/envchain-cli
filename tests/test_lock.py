import time
import pytest
from pathlib import Path
from envchain.lock import (
    lock_store, unlock_store, get_unlocked_passphrase, is_locked, session_remaining
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / "store" / ".envchain"
    store_file.parent.mkdir()
    store_file.write_text("{}")
    return str(store_file)


def test_initially_locked(store):
    assert is_locked(store)


def test_unlock_allows_passphrase_retrieval(store):
    unlock_store(store, "secret", ttl_seconds=60)
    assert get_unlocked_passphrase(store) == "secret"


def test_lock_clears_session(store):
    unlock_store(store, "secret", ttl_seconds=60)
    lock_store(store)
    assert is_locked(store)


def test_expired_session_returns_none(store):
    unlock_store(store, "secret", ttl_seconds=-1)
    assert get_unlocked_passphrase(store) is None


def test_session_remaining_positive(store):
    unlock_store(store, "secret", ttl_seconds=120)
    remaining = session_remaining(store)
    assert 0 < remaining <= 120


def test_session_remaining_locked(store):
    assert session_remaining(store) == 0.0


def test_lock_idempotent(store):
    lock_store(store)
    lock_store(store)  # should not raise
    assert is_locked(store)


def test_unlock_overwrites_existing_session(store):
    unlock_store(store, "first", ttl_seconds=60)
    unlock_store(store, "second", ttl_seconds=60)
    assert get_unlocked_passphrase(store) == "second"
