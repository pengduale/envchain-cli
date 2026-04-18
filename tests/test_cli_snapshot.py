"""Tests for CLI snapshot commands."""
import pytest
from click.testing import CliRunner
from pathlib import Path
from envchain.store import set_variable
from envchain.cli import cli

PASS = "clisnap"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "store.json"
    set_variable(p, "FOO", "bar", PASS)
    set_variable(p, "BAZ", "qux", PASS)
    return p


def invoke(runner, store_path, *args):
    return runner.invoke(cli, ["--store", str(store_path), "--passphrase", PASS, *args])


def test_snapshot_create(runner, store_path):
    result = invoke(runner, store_path, "snapshot", "create")
    assert result.exit_code == 0
    assert "Snapshot created" in result.output


def test_snapshot_create_with_label(runner, store_path):
    result = invoke(runner, store_path, "snapshot", "create", "--label", "v1")
    assert "v1" in result.output


def test_snapshot_list_empty(runner, store_path):
    result = invoke(runner, store_path, "snapshot", "list")
    assert "No snapshots" in result.output


def test_snapshot_list_shows_entries(runner, store_path):
    invoke(runner, store_path, "snapshot", "create", "--label", "alpha")
    result = invoke(runner, store_path, "snapshot", "list")
    assert "alpha" in result.output
    assert "FOO" in result.output


def test_snapshot_restore(runner, store_path):
    invoke(runner, store_path, "snapshot", "create")
    snaps = __import__("envchain.snapshot", fromlist=["list_snapshots"]).list_snapshots(store_path)
    name = snaps[0]["file"]
    result = invoke(runner, store_path, "snapshot", "restore", name)
    assert "Restored 2" in result.output


def test_snapshot_delete(runner, store_path):
    invoke(runner, store_path, "snapshot", "create")
    snaps = __import__("envchain.snapshot", fromlist=["list_snapshots"]).list_snapshots(store_path)
    name = snaps[0]["file"]
    result = invoke(runner, store_path, "snapshot", "delete", name)
    assert "deleted" in result.output
