"""Tests for envchain.snapshot."""
import pytest
from pathlib import Path
from envchain.store import set_variable
from envchain.snapshot import (
    create_snapshot, list_snapshots, restore_snapshot, delete_snapshot
)

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    p = tmp_path / "store.json"
    set_variable(p, "KEY1", "val1", PASS)
    set_variable(p, "KEY2", "val2", PASS)
    return p


def test_create_snapshot_returns_path(store):
    snap = create_snapshot(store, PASS)
    assert snap.exists()
    assert snap.suffix == ".json"


def test_create_snapshot_with_label(store):
    snap = create_snapshot(store, PASS, label="before-deploy")
    assert "before-deploy" in snap.name


def test_create_snapshot_empty_store_raises(tmp_path):
    empty = tmp_path / "empty.json"
    with pytest.raises(ValueError, match="empty"):
        create_snapshot(empty, PASS)


def test_list_snapshots_empty(store):
    result = list_snapshots(store)
    assert result == []


def test_list_snapshots_after_create(store):
    create_snapshot(store, PASS, label="snap1")
    create_snapshot(store, PASS, label="snap2")
    snaps = list_snapshots(store)
    assert len(snaps) == 2
    labels = [s["label"] for s in snaps]
    assert "snap1" in labels and "snap2" in labels


def test_restore_snapshot_overwrites(store):
    snap = create_snapshot(store, PASS)
    set_variable(store, "KEY1", "changed", PASS)
    count = restore_snapshot(store, snap.name, PASS)
    assert count == 2
    from envchain.store import get_variable
    assert get_variable(store, "KEY1", PASS) == "val1"


def test_restore_missing_snapshot_raises(store):
    with pytest.raises(FileNotFoundError):
        restore_snapshot(store, "nonexistent.json", PASS)


def test_delete_snapshot(store):
    snap = create_snapshot(store, PASS)
    delete_snapshot(store, snap.name)
    assert list_snapshots(store) == []


def test_delete_missing_snapshot_raises(store):
    with pytest.raises(FileNotFoundError):
        delete_snapshot(store, "ghost.json")
