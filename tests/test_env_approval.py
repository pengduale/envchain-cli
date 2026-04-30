"""Tests for envchain.env_approval."""

import pytest
from pathlib import Path
from envchain.env_approval import (
    set_approval, get_approval, remove_approval, list_approvals
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_approval(store):
    result = set_approval(store, "MY_KEY", "pending", approver="alice")
    assert result.ok
    assert result.status == "pending"
    assert result.approver == "alice"
    assert result.timestamp is not None


def test_get_approval_after_set(store):
    set_approval(store, "MY_KEY", "approved", approver="bob")
    r = get_approval(store, "MY_KEY")
    assert r is not None
    assert r.status == "approved"
    assert r.approver == "bob"


def test_get_missing_approval_returns_none(store):
    assert get_approval(store, "MISSING_KEY") is None


def test_invalid_status_returns_error(store):
    result = set_approval(store, "MY_KEY", "unknown")
    assert not result.ok
    assert "Invalid status" in result.message


def test_empty_key_returns_error(store):
    result = set_approval(store, "", "approved")
    assert not result.ok
    assert "empty" in result.message.lower()


def test_overwrite_approval(store):
    set_approval(store, "MY_KEY", "pending")
    set_approval(store, "MY_KEY", "approved", approver="charlie")
    r = get_approval(store, "MY_KEY")
    assert r.status == "approved"
    assert r.approver == "charlie"


def test_remove_approval_returns_true(store):
    set_approval(store, "MY_KEY", "rejected")
    assert remove_approval(store, "MY_KEY") is True
    assert get_approval(store, "MY_KEY") is None


def test_remove_missing_approval_returns_false(store):
    assert remove_approval(store, "NONEXISTENT") is False


def test_list_approvals_empty(store):
    assert list_approvals(store) == []


def test_list_approvals_multiple(store):
    set_approval(store, "KEY_A", "pending")
    set_approval(store, "KEY_B", "approved")
    set_approval(store, "KEY_C", "rejected")
    results = list_approvals(store)
    assert len(results) == 3
    keys = {r.key for r in results}
    assert keys == {"KEY_A", "KEY_B", "KEY_C"}


def test_list_approvals_with_status_filter(store):
    set_approval(store, "KEY_A", "pending")
    set_approval(store, "KEY_B", "approved")
    set_approval(store, "KEY_C", "pending")
    results = list_approvals(store, status_filter="pending")
    assert len(results) == 2
    assert all(r.status == "pending" for r in results)


def test_approval_message_stored(store):
    set_approval(store, "MY_KEY", "rejected", message="Needs review")
    r = get_approval(store, "MY_KEY")
    assert r.message == "Needs review"
