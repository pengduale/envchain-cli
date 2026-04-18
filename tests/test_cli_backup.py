"""Tests for envchain.cli_backup."""

import pytest
from click.testing import CliRunner
from pathlib import Path
import click

from envchain.cli_backup import register_backup_commands
from envchain.backup import create_backup


@pytest.fixture
def store_path(tmp_path):
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    (store_dir / "vars.json").write_text('{"KEY": "enc"}')
    return str(store_dir)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)
        ctx.obj["store_path"] = store_path

    def get_store(ctx):
        return ctx.obj["store_path"]

    register_backup_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_backup_create(runner, cli):
    result = invoke(runner, cli, "backup", "create")
    assert result.exit_code == 0
    assert "Backup created" in result.output


def test_backup_create_with_label(runner, cli):
    result = invoke(runner, cli, "backup", "create", "--label", "myrelease")
    assert "myrelease" in result.output


def test_backup_list_empty(runner, cli):
    result = invoke(runner, cli, "backup", "list")
    assert "No backups found" in result.output


def test_backup_list_shows_entry(runner, cli, store_path):
    create_backup(store_path, label="ci")
    result = invoke(runner, cli, "backup", "list")
    assert "ci" in result.output


def test_backup_delete_missing(runner, cli):
    result = runner.invoke(cli, ["backup", "delete", "/no/such/file.tar.gz"])
    assert result.exit_code != 0


def test_backup_restore_no_overwrite(runner, cli, store_path, tmp_path):
    archive = create_backup(store_path)
    target = str(tmp_path / "out")
    result = invoke(runner, cli, "backup", "restore", archive, target)
    assert result.exit_code == 0
    assert Path(target).exists()
