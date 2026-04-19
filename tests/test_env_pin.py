import pytest
from pathlib import Path
from envchain.env_pin import pin_variable, unpin_variable, get_pin, list_pins


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_pin_variable_returns_success(store):
    result = pin_variable(store, "API_KEY", "snap-001")
    assert result.success is True
    assert result.key == "API_KEY"
    assert result.snapshot_id == "snap-001"


def test_get_pin_returns_snapshot_id(store):
    pin_variable(store, "API_KEY", "snap-001")
    assert get_pin(store, "API_KEY") == "snap-001"


def test_get_pin_missing_returns_none(store):
    assert get_pin(store, "MISSING") is None


def test_pin_overwrite(store):
    pin_variable(store, "API_KEY", "snap-001")
    pin_variable(store, "API_KEY", "snap-002")
    assert get_pin(store, "API_KEY") == "snap-002"


def test_unpin_removes_pin(store):
    pin_variable(store, "API_KEY", "snap-001")
    result = unpin_variable(store, "API_KEY")
    assert result.success is True
    assert result.snapshot_id == "snap-001"
    assert get_pin(store, "API_KEY") is None


def test_unpin_missing_key_fails(store):
    result = unpin_variable(store, "GHOST")
    assert result.success is False
    assert "not pinned" in result.message


def test_list_pins_empty(store):
    assert list_pins(store) == {}


def test_list_pins_multiple(store):
    pin_variable(store, "KEY_A", "snap-001")
    pin_variable(store, "KEY_B", "snap-002")
    pins = list_pins(store)
    assert pins == {"KEY_A": "snap-001", "KEY_B": "snap-002"}


def test_pins_are_profile_isolated(store):
    pin_variable(store, "KEY", "snap-001", profile="dev")
    pin_variable(store, "KEY", "snap-999", profile="prod")
    assert get_pin(store, "KEY", profile="dev") == "snap-001"
    assert get_pin(store, "KEY", profile="prod") == "snap-999"


def test_list_pins_profile_specific(store):
    pin_variable(store, "KEY", "snap-001", profile="dev")
    pin_variable(store, "OTHER", "snap-002", profile="prod")
    assert "KEY" in list_pins(store, profile="dev")
    assert "OTHER" not in list_pins(store, profile="dev")
