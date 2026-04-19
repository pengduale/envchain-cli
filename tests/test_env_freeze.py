"""Tests for envchain.env_freeze."""
import os
import pytest
from pathlib import Path

from envchain.store import set_variable, get_variable, list_keys
from envchain.env_freeze import freeze_from_env, thaw_to_env, FreezeResult

PASS = "test-pass"


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_freeze_captures_env_var(store, monkeypatch):
    monkeypatch.setenv("MY_TOKEN", "abc123")
    result = freeze_from_env(store, PASS, keys=["MY_TOKEN"])
    assert "MY_TOKEN" in result.frozen
    assert get_variable(store, "MY_TOKEN", PASS) == "abc123"


def test_freeze_skips_missing_env_var(store, monkeypatch):
    monkeypatch.delenv("GHOST_VAR", raising=False)
    result = freeze_from_env(store, PASS, keys=["GHOST_VAR"])
    assert "GHOST_VAR" in result.skipped
    assert "GHOST_VAR" not in result.frozen


def test_freeze_skips_existing_without_overwrite(store, monkeypatch):
    monkeypatch.setenv("DB_URL", "new-value")
    set_variable(store, "DB_URL", "old-value", PASS)
    result = freeze_from_env(store, PASS, keys=["DB_URL"], overwrite=False)
    assert "DB_URL" in result.skipped
    assert get_variable(store, "DB_URL", PASS) == "old-value"


def test_freeze_overwrites_when_flag_set(store, monkeypatch):
    monkeypatch.setenv("DB_URL", "new-value")
    set_variable(store, "DB_URL", "old-value", PASS)
    result = freeze_from_env(store, PASS, keys=["DB_URL"], overwrite=True)
    assert "DB_URL" in result.frozen
    assert get_variable(store, "DB_URL", PASS) == "new-value"


def test_freeze_with_prefix(store, monkeypatch):
    monkeypatch.setenv("APP_SECRET", "s3cr3t")
    monkeypatch.setenv("APP_KEY", "key1")
    monkeypatch.setenv("OTHER_VAR", "nope")
    result = freeze_from_env(store, PASS, prefix="APP_")
    assert "APP_SECRET" in result.frozen
    assert "APP_KEY" in result.frozen
    assert "OTHER_VAR" not in result.frozen


def test_freeze_repr():
    r = FreezeResult(frozen=["A", "B"], skipped=["C"], profile="staging")
    assert "staging" in repr(r)
    assert "frozen=2" in repr(r)


def test_thaw_returns_all_stored(store):
    set_variable(store, "K1", "v1", PASS)
    set_variable(store, "K2", "v2", PASS)
    result = thaw_to_env(store, PASS)
    assert result["K1"] == "v1"
    assert result["K2"] == "v2"


def test_thaw_empty_store(store):
    result = thaw_to_env(store, PASS)
    assert result == {}
