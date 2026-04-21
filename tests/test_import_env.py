import os
import pytest
from unittest.mock import patch

from envchain.import_env import import_from_env, list_importable, _is_valid_key


FAKE_ENV = {
    "MY_APP_SECRET": "abc123",
    "MY_APP_KEY": "keyval",
    "OTHER_VAR": "other",
    "lowercase_var": "nope",
    "VALID_ONE": "yes",
}


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_is_valid_key_accepts_uppercase():
    assert _is_valid_key("MY_VAR") is True
    assert _is_valid_key("VAR123") is True
    assert _is_valid_key("_PRIVATE") is True


def test_is_valid_key_rejects_lowercase():
    assert _is_valid_key("my_var") is False
    assert _is_valid_key("Mixed") is False


def test_list_importable_no_prefix():
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        result = list_importable()
    assert "MY_APP_SECRET" in result
    assert "lowercase_var" not in result


def test_list_importable_with_prefix():
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        result = list_importable(prefix="MY_APP_")
    assert set(result) == {"MY_APP_SECRET", "MY_APP_KEY"}


def test_import_with_prefix(store):
    passphrase = "testpass"
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        imported = import_from_env(store, passphrase, prefix="MY_APP_")
    keys = [stored for _, stored in imported]
    assert "MY_APP_SECRET" in keys
    assert "MY_APP_KEY" in keys
    assert "OTHER_VAR" not in keys


def test_import_strips_prefix(store):
    passphrase = "testpass"
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        imported = import_from_env(store, passphrase, prefix="MY_APP_", strip_prefix=True)
    stored_names = [stored for _, stored in imported]
    assert "SECRET" in stored_names
    assert "KEY" in stored_names


def test_import_explicit_keys(store):
    passphrase = "testpass"
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        imported = import_from_env(store, passphrase, keys=["MY_APP_SECRET", "VALID_ONE"])
    assert len(imported) == 2
    assert {orig for orig, _ in imported} == {"MY_APP_SECRET", "VALID_ONE"}


def test_import_missing_explicit_key_skipped(store):
    passphrase = "testpass"
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        imported = import_from_env(store, passphrase, keys=["DOES_NOT_EXIST"])
    assert imported == []


def test_import_values_readable(store):
    from envchain.store import get_variable
    passphrase = "testpass"
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        import_from_env(store, passphrase, keys=["MY_APP_SECRET"])
    val = get_variable(store, passphrase, "MY_APP_SECRET")
    assert val == "abc123"


def test_import_returns_original_and_stored_name(store):
    """Each entry in the returned list should be a (original_name, stored_name) tuple."""
    passphrase = "testpass"
    with patch.dict(os.environ, FAKE_ENV, clear=True):
        imported = import_from_env(store, passphrase, keys=["MY_APP_SECRET"])
    assert len(imported) == 1
    orig, stored = imported[0]
    assert orig == "MY_APP_SECRET"
    assert stored == "MY_APP_SECRET"
