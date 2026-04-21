"""Tests for envchain.env_expiry_policy."""

import pytest

from envchain.env_expiry_policy import (
    ExpiryPolicyResult,
    get_expiry_policy,
    list_expiry_policies,
    remove_expiry_policy,
    set_expiry_policy,
)


@pytest.fixture()
def store(tmp_path):
    return tmp_path


def test_set_and_get_policy(store):
    result = set_expiry_policy(store, "API_KEY", max_age_days=30)
    assert isinstance(result, ExpiryPolicyResult)
    assert result.ok is True
    assert result.key == "API_KEY"
    assert result.max_age_days == 30
    assert result.action == "warn"

    policy = get_expiry_policy(store, "API_KEY")
    assert policy is not None
    assert policy["max_age_days"] == 30
    assert policy["warn_before_days"] == 3
    assert policy["action"] == "warn"


def test_get_missing_policy_returns_none(store):
    assert get_expiry_policy(store, "MISSING") is None


def test_set_policy_with_custom_warn_and_action(store):
    result = set_expiry_policy(store, "SECRET", max_age_days=90, warn_before_days=7, action="delete")
    assert result.warn_before_days == 7
    assert result.action == "delete"
    policy = get_expiry_policy(store, "SECRET")
    assert policy["action"] == "delete"


def test_set_policy_invalid_action_raises(store):
    with pytest.raises(ValueError, match="Invalid action"):
        set_expiry_policy(store, "KEY", max_age_days=10, action="explode")


def test_set_policy_invalid_max_age_raises(store):
    with pytest.raises(ValueError, match="max_age_days"):
        set_expiry_policy(store, "KEY", max_age_days=0)


def test_set_policy_negative_warn_before_raises(store):
    with pytest.raises(ValueError, match="warn_before_days"):
        set_expiry_policy(store, "KEY", max_age_days=10, warn_before_days=-1)


def test_overwrite_policy(store):
    set_expiry_policy(store, "DB_PASS", max_age_days=30, action="warn")
    set_expiry_policy(store, "DB_PASS", max_age_days=60, action="lock")
    policy = get_expiry_policy(store, "DB_PASS")
    assert policy["max_age_days"] == 60
    assert policy["action"] == "lock"


def test_remove_policy_returns_true(store):
    set_expiry_policy(store, "TOKEN", max_age_days=14)
    assert remove_expiry_policy(store, "TOKEN") is True
    assert get_expiry_policy(store, "TOKEN") is None


def test_remove_missing_policy_returns_false(store):
    assert remove_expiry_policy(store, "NONEXISTENT") is False


def test_list_policies_empty(store):
    assert list_expiry_policies(store) == {}


def test_list_policies_multiple(store):
    set_expiry_policy(store, "A", max_age_days=10)
    set_expiry_policy(store, "B", max_age_days=20, action="delete")
    policies = list_expiry_policies(store)
    assert set(policies.keys()) == {"A", "B"}
    assert policies["B"]["action"] == "delete"


def test_repr_contains_key(store):
    result = set_expiry_policy(store, "MY_KEY", max_age_days=7)
    assert "MY_KEY" in repr(result)
    assert "warn" in repr(result)
