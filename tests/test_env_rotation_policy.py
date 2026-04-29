"""Tests for envchain.env_rotation_policy."""

import pytest
from pathlib import Path
from envchain.env_rotation_policy import (
    set_rotation_policy,
    get_rotation_policy,
    remove_rotation_policy,
    list_rotation_policies,
    VALID_INTERVALS,
)


@pytest.fixture
def store(tmp_path: Path) -> Path:
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    return store_dir


def test_set_and_get_policy(store):
    result = set_rotation_policy(store, "API_KEY", "monthly")
    assert result.ok
    assert result.key == "API_KEY"
    assert result.interval == "monthly"
    assert result.notify_before_days == 7

    fetched = get_rotation_policy(store, "API_KEY")
    assert fetched is not None
    assert fetched.interval == "monthly"
    assert fetched.notify_before_days == 7


def test_get_missing_policy_returns_none(store):
    assert get_rotation_policy(store, "MISSING_KEY") is None


def test_set_policy_with_custom_notify(store):
    result = set_rotation_policy(store, "DB_PASS", "weekly", notify_before_days=3)
    assert result.ok
    fetched = get_rotation_policy(store, "DB_PASS")
    assert fetched.notify_before_days == 3


def test_overwrite_policy(store):
    set_rotation_policy(store, "TOKEN", "daily")
    set_rotation_policy(store, "TOKEN", "yearly", notify_before_days=14)
    fetched = get_rotation_policy(store, "TOKEN")
    assert fetched.interval == "yearly"
    assert fetched.notify_before_days == 14


def test_invalid_interval_returns_error(store):
    result = set_rotation_policy(store, "KEY", "hourly")
    assert not result.ok
    assert "hourly" in result.error


def test_empty_key_returns_error(store):
    result = set_rotation_policy(store, "", "daily")
    assert not result.ok
    assert "empty" in result.error.lower()


def test_negative_notify_days_returns_error(store):
    result = set_rotation_policy(store, "KEY", "monthly", notify_before_days=-1)
    assert not result.ok
    assert "notify_before_days" in result.error


def test_remove_policy_returns_true(store):
    set_rotation_policy(store, "SECRET", "quarterly")
    assert remove_rotation_policy(store, "SECRET") is True
    assert get_rotation_policy(store, "SECRET") is None


def test_remove_missing_policy_returns_false(store):
    assert remove_rotation_policy(store, "NONEXISTENT") is False


def test_list_policies_empty(store):
    assert list_rotation_policies(store) == []


def test_list_policies_multiple(store):
    set_rotation_policy(store, "A", "daily")
    set_rotation_policy(store, "B", "monthly", notify_before_days=5)
    policies = list_rotation_policies(store)
    assert len(policies) == 2
    keys = {p.key for p in policies}
    assert keys == {"A", "B"}


def test_all_valid_intervals_accepted(store):
    for i, interval in enumerate(VALID_INTERVALS):
        key = f"KEY_{i}"
        result = set_rotation_policy(store, key, interval)
        assert result.ok, f"Expected {interval} to be valid"


def test_repr_ok(store):
    result = set_rotation_policy(store, "MY_KEY", "weekly")
    assert "MY_KEY" in repr(result)
    assert "weekly" in repr(result)


def test_repr_error():
    from envchain.env_rotation_policy import RotationPolicyResult
    r = RotationPolicyResult(key="X", interval="bad", notify_before_days=0, ok=False, error="oops")
    assert "oops" in repr(r)
