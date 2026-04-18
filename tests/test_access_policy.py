import pytest
import json
from pathlib import Path
from envchain.access_policy import (
    set_policy, remove_policy, get_policy, list_policies, can_read, can_write
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_set_and_get_policy(store):
    set_policy(store, "ci", allow_read=["API_KEY"], allow_write=[])
    p = get_policy(store, "ci")
    assert p["allow_read"] == ["API_KEY"]
    assert p["allow_write"] == []


def test_get_missing_policy_returns_none(store):
    assert get_policy(store, "ghost") is None


def test_list_policies_empty(store):
    assert list_policies(store) == []


def test_list_policies_multiple(store):
    set_policy(store, "ci", ["A"], [])
    set_policy(store, "dev", ["*"], ["*"])
    assert set(list_policies(store)) == {"ci", "dev"}


def test_overwrite_policy(store):
    set_policy(store, "ci", ["OLD"], [])
    set_policy(store, "ci", ["NEW"], ["NEW"])
    p = get_policy(store, "ci")
    assert p["allow_read"] == ["NEW"]


def test_remove_policy(store):
    set_policy(store, "ci", ["A"], [])
    assert remove_policy(store, "ci") is True
    assert get_policy(store, "ci") is None


def test_remove_missing_policy_returns_false(store):
    assert remove_policy(store, "nobody") is False


def test_can_read_allowed_key(store):
    set_policy(store, "ci", allow_read=["API_KEY", "DB_URL"], allow_write=[])
    assert can_read(store, "ci", "API_KEY") is True
    assert can_read(store, "ci", "SECRET") is False


def test_can_read_wildcard(store):
    set_policy(store, "admin", allow_read=["*"], allow_write=["*"])
    assert can_read(store, "admin", "ANYTHING") is True


def test_can_write_denied(store):
    set_policy(store, "readonly", allow_read=["*"], allow_write=[])
    assert can_write(store, "readonly", "API_KEY") is False


def test_can_read_unknown_role(store):
    assert can_read(store, "unknown", "KEY") is False


def test_policy_persisted_to_file(store):
    set_policy(store, "ci", ["X"], [])
    raw = json.loads((Path(store) / ".envchain_policy.json").read_text())
    assert "ci" in raw
