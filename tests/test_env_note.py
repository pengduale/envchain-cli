import pytest
import tempfile
import os
from envchain.env_note import set_note, get_note, remove_note, list_notes, keys_with_notes


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_set_and_get_note(store):
    set_note(store, "API_KEY", "Production API key")
    assert get_note(store, "API_KEY") == "Production API key"


def test_get_missing_note_returns_none(store):
    assert get_note(store, "MISSING") is None


def test_overwrite_note(store):
    set_note(store, "KEY", "old note")
    set_note(store, "KEY", "new note")
    assert get_note(store, "KEY") == "new note"


def test_remove_note_returns_true(store):
    set_note(store, "KEY", "some note")
    assert remove_note(store, "KEY") is True
    assert get_note(store, "KEY") is None


def test_remove_missing_note_returns_false(store):
    assert remove_note(store, "NONEXISTENT") is False


def test_list_notes_empty(store):
    assert list_notes(store) == {}


def test_list_notes_multiple(store):
    set_note(store, "A", "note a")
    set_note(store, "B", "note b")
    notes = list_notes(store)
    assert notes == {"A": "note a", "B": "note b"}


def test_keys_with_notes(store):
    set_note(store, "X", "x note")
    set_note(store, "Y", "y note")
    keys = keys_with_notes(store)
    assert set(keys) == {"X", "Y"}


def test_notes_persist_across_calls(store):
    set_note(store, "PERSIST", "persistent note")
    # Simulate re-loading by calling get_note freshly
    result = get_note(store, "PERSIST")
    assert result == "persistent note"
