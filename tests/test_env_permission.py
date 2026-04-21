import pytest
from pathlib import Path
from envchain.env_permission import (
    set_permissions,
    get_permissions,
    remove_permissions,
    has_permission,
    list_permissions,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_set_and_get_permissions(store):
    result = set_permissions(store, "API_KEY", ["read", "write"])
    assert result.ok
    assert sorted(result.permissions) == ["read", "write"]


def test_get_permissions_after_set(store):
    set_permissions(store, "DB_PASS", ["read"])
    perms = get_permissions(store, "DB_PASS")
    assert perms == ["read"]


def test_get_missing_permissions_returns_none(store):
    assert get_permissions(store, "MISSING") is None


def test_set_permissions_invalid_raises(store):
    with pytest.raises(ValueError, match="Invalid permissions"):
        set_permissions(store, "KEY", ["read", "execute"])


def test_set_permissions_empty_raises(store):
    with pytest.raises(ValueError, match="must not be empty"):
        set_permissions(store, "KEY", [])


def test_set_permissions_deduplicates(store):
    result = set_permissions(store, "KEY", ["read", "read", "write"])
    assert result.permissions == ["read", "write"]


def test_overwrite_permissions(store):
    set_permissions(store, "KEY", ["read", "write", "delete"])
    set_permissions(store, "KEY", ["read"])
    assert get_permissions(store, "KEY") == ["read"]


def test_remove_permissions_returns_true(store):
    set_permissions(store, "KEY", ["read"])
    assert remove_permissions(store, "KEY") is True
    assert get_permissions(store, "KEY") is None


def test_remove_missing_permissions_returns_false(store):
    assert remove_permissions(store, "GHOST") is False


def test_has_permission_unrestricted_key_returns_true(store):
    assert has_permission(store, "FREE_KEY", "read") is True
    assert has_permission(store, "FREE_KEY", "delete") is True


def test_has_permission_restricted_key(store):
    set_permissions(store, "SECRET", ["read"])
    assert has_permission(store, "SECRET", "read") is True
    assert has_permission(store, "SECRET", "write") is False
    assert has_permission(store, "SECRET", "delete") is False


def test_list_permissions_empty(store):
    assert list_permissions(store) == {}


def test_list_permissions_multiple_keys(store):
    set_permissions(store, "A", ["read"])
    set_permissions(store, "B", ["read", "write"])
    result = list_permissions(store)
    assert "A" in result
    assert "B" in result
    assert result["A"] == ["read"]
