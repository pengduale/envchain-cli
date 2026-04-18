import pytest
from pathlib import Path
from envchain.hooks import add_hook, remove_hook, list_hooks, fire_hook, HOOK_EVENTS


@pytest.fixture
def store(tmp_path):
    return str(tmp_path)


def test_add_hook_creates_entry(store):
    add_hook(store, "post-set", "echo")
    hooks = list_hooks(store)
    assert "echo" in hooks.get("post-set", [])


def test_add_hook_no_duplicates(store):
    add_hook(store, "post-set", "echo")
    add_hook(store, "post-set", "echo")
    assert list_hooks(store)["post-set"].count("echo") == 1


def test_add_hook_invalid_event_raises(store):
    with pytest.raises(ValueError):
        add_hook(store, "invalid-event", "echo")


def test_remove_hook_returns_true(store):
    add_hook(store, "pre-get", "logger")
    result = remove_hook(store, "pre-get", "logger")
    assert result is True
    assert "logger" not in list_hooks(store).get("pre-get", [])


def test_remove_missing_hook_returns_false(store):
    result = remove_hook(store, "pre-get", "nonexistent")
    assert result is False


def test_list_hooks_empty(store):
    assert list_hooks(store) == {}


def test_list_hooks_filtered_by_event(store):
    add_hook(store, "post-set", "cmd1")
    add_hook(store, "post-delete", "cmd2")
    result = list_hooks(store, "post-set")
    assert "post-set" in result
    assert "post-delete" not in result


def test_multiple_hooks_same_event(store):
    add_hook(store, "post-set", "cmd1")
    add_hook(store, "post-set", "cmd2")
    cmds = list_hooks(store)["post-set"]
    assert "cmd1" in cmds
    assert "cmd2" in cmds


def test_fire_hook_returns_executed(store):
    add_hook(store, "post-set", "echo")
    executed = fire_hook(store, "post-set", "MY_KEY")
    assert len(executed) == 1
    assert "MY_KEY" in executed[0]


def test_fire_hook_no_hooks_registered(store):
    executed = fire_hook(store, "post-set", "MY_KEY")
    assert executed == []
