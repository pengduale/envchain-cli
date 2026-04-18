"""Tests for envchain.backup."""

import os
import pytest
from pathlib import Path

from envchain.backup import (
    create_backup,
    delete_backup,
    list_backups,
    restore_backup,
)


@pytest.fixture
def store(tmp_path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    (store_dir / "vars.json").write_text('{"KEY": "val"}')
    return str(store_dir)


def test_create_backup_returns_path(store):
    path = create_backup(store)
    assert path.endswith(".tar.gz")
    assert Path(path).exists()


def test_create_backup_with_label(store):
    path = create_backup(store, label="release")
    assert "release" in path


def test_create_backup_missing_store(tmp_path):
    with pytest.raises(FileNotFoundError):
        create_backup(str(tmp_path / "nonexistent"))


def test_list_backups_empty(store):
    assert list_backups(store) == []


def test_list_backups_after_create(store):
    create_backup(store, label="v1")
    backups = list_backups(store)
    assert len(backups) == 1
    assert backups[0]["label"] == "v1"
    assert backups[0]["exists"] is True


def test_list_backups_multiple(store):
    create_backup(store)
    create_backup(store, label="second")
    assert len(list_backups(store)) == 2


def test_restore_backup(store, tmp_path):
    path = create_backup(store)
    target = str(tmp_path / "restored")
    restore_backup(path, target)
    assert (Path(target) / "vars.json").exists()


def test_restore_backup_overwrite(store, tmp_path):
    path = create_backup(store)
    target = str(tmp_path / "restored")
    restore_backup(path, target)
    restore_backup(path, target, overwrite=True)
    assert (Path(target) / "vars.json").exists()


def test_restore_backup_no_overwrite_raises(store, tmp_path):
    path = create_backup(store)
    target = str(tmp_path / "restored")
    restore_backup(path, target)
    with pytest.raises(FileExistsError):
        restore_backup(path, target, overwrite=False)


def test_delete_backup(store):
    path = create_backup(store)
    assert delete_backup(path) is True
    assert not Path(path).exists()


def test_delete_backup_missing(store):
    assert delete_backup("/nonexistent/backup.tar.gz") is False
