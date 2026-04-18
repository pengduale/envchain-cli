import pytest
from pathlib import Path
from envchain.alias import set_alias, remove_alias, resolve_alias, list_aliases


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_set_and_resolve(store):
    set_alias(store, "db", "DATABASE_URL")
    assert resolve_alias(store, "db") == "DATABASE_URL"


def test_resolve_missing_returns_none(store):
    assert resolve_alias(store, "nope") is None


def test_overwrite_alias(store):
    set_alias(store, "db", "DATABASE_URL")
    set_alias(store, "db", "DB_URI")
    assert resolve_alias(store, "db") == "DB_URI"


def test_remove_alias(store):
    set_alias(store, "db", "DATABASE_URL")
    remove_alias(store, "db")
    assert resolve_alias(store, "db") is None


def test_remove_missing_raises(store):
    with pytest.raises(KeyError, match="not found"):
        remove_alias(store, "ghost")


def test_list_aliases_empty(store):
    assert list_aliases(store) == {}


def test_list_aliases_multiple(store):
    set_alias(store, "db", "DATABASE_URL")
    set_alias(store, "redis", "REDIS_URL")
    result = list_aliases(store)
    assert result == {"db": "DATABASE_URL", "redis": "REDIS_URL"}


def test_aliases_file_created(store):
    set_alias(store, "x", "X_VAR")
    assert (Path(store) / ".aliases.json").exists()
