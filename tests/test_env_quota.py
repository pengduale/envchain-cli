"""Tests for envchain.env_quota."""

from __future__ import annotations

import pytest
from pathlib import Path

from envchain.env_quota import (
    check_quota,
    get_quota,
    list_quotas,
    remove_quota,
    set_quota,
)


@pytest.fixture
def store(tmp_path):
    store_file = tmp_path / ".envchain.json"
    store_file.write_text("{}")
    return store_file


def test_set_and_get_quota(store):
    result = set_quota(store, "default", 10)
    assert result.ok
    assert result.limit == 10
    assert get_quota(store, "default") == 10


def test_get_missing_quota_returns_none(store):
    assert get_quota(store, "nonexistent") is None


def test_set_quota_invalid_limit_raises(store):
    with pytest.raises(ValueError):
        set_quota(store, "default", 0)


def test_remove_quota_returns_true(store):
    set_quota(store, "staging", 5)
    assert remove_quota(store, "staging") is True
    assert get_quota(store, "staging") is None


def test_remove_missing_quota_returns_false(store):
    assert remove_quota(store, "ghost") is False


def test_check_quota_no_limit_always_ok(store):
    result = check_quota(store, "default", 999)
    assert result.ok
    assert result.limit is None


def test_check_quota_within_limit(store):
    set_quota(store, "prod", 5)
    result = check_quota(store, "prod", 4)
    assert result.ok
    assert result.current == 4
    assert result.limit == 5


def test_check_quota_at_limit_fails(store):
    set_quota(store, "prod", 3)
    result = check_quota(store, "prod", 3)
    assert not result.ok
    assert "exceeded" in result.message.lower()


def test_check_quota_over_limit_fails(store):
    set_quota(store, "prod", 3)
    result = check_quota(store, "prod", 10)
    assert not result.ok


def test_list_quotas_empty(store):
    assert list_quotas(store) == {}


def test_list_quotas_multiple(store):
    set_quota(store, "dev", 20)
    set_quota(store, "prod", 5)
    quotas = list_quotas(store)
    assert quotas == {"dev": 20, "prod": 5}


def test_overwrite_quota(store):
    set_quota(store, "default", 10)
    set_quota(store, "default", 50)
    assert get_quota(store, "default") == 50
