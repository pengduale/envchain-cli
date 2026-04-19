import pytest
from pathlib import Path
from envchain.env_mask import (
    mask_variable,
    unmask_variable,
    is_masked,
    list_masked,
    apply_mask,
)


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_mask_variable_returns_result(store):
    result = mask_variable(store, "API_KEY")
    assert result.key == "API_KEY"
    assert result.masked is True


def test_is_masked_after_mask(store):
    mask_variable(store, "SECRET")
    assert is_masked(store, "SECRET") is True


def test_is_masked_default_false(store):
    assert is_masked(store, "NOT_MASKED") is False


def test_unmask_variable(store):
    mask_variable(store, "TOKEN")
    result = unmask_variable(store, "TOKEN")
    assert result.masked is False
    assert is_masked(store, "TOKEN") is False


def test_unmask_nonexistent_key(store):
    result = unmask_variable(store, "GHOST")
    assert result.masked is False


def test_list_masked_empty(store):
    assert list_masked(store) == []


def test_list_masked_multiple(store):
    mask_variable(store, "A")
    mask_variable(store, "B")
    keys = list_masked(store)
    assert set(keys) == {"A", "B"}


def test_list_masked_excludes_unmasked(store):
    mask_variable(store, "A")
    mask_variable(store, "B")
    unmask_variable(store, "A")
    keys = list_masked(store)
    assert keys == ["B"]


def test_apply_mask_hides_value(store):
    mask_variable(store, "PWD")
    assert apply_mask(store, "PWD", "super_secret") == "****"


def test_apply_mask_shows_value_when_not_masked(store):
    assert apply_mask(store, "VISIBLE", "hello") == "hello"


def test_mask_creates_file(store):
    mask_variable(store, "X")
    assert (Path(store) / ".mask.json").exists()
