"""CLI tests for lifecycle commands."""

import pytest
from click.testing import CliRunner
import click
from pathlib import Path

from envchain.cli_env_lifecycle import register_lifecycle_commands
from envchain.env_lifecycle import set_lifecycle


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / "store.json"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    def root():
        pass

    def get_store(ctx):
        return store_path

    register_lifecycle_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_lifecycle_set(runner, cli):
    result = invoke(runner, cli, ["lifecycle", "set", "API_KEY", "active"])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_lifecycle_get_unset(runner, cli):
    result = invoke(runner, cli, ["lifecycle", "get", "MISSING"])
    assert result.exit_code == 0
    assert "unset" in result.output


def test_lifecycle_get_after_set(runner, cli, store_path):
    set_lifecycle(store_path, "DB_URL", "deprecated")
    result = invoke(runner, cli, ["lifecycle", "get", "DB_URL"])
    assert result.exit_code == 0
    assert "deprecated" in result.output


def test_lifecycle_remove_existing(runner, cli, store_path):
    set_lifecycle(store_path, "TOKEN", "retired")
    result = invoke(runner, cli, ["lifecycle", "remove", "TOKEN"])
    assert result.exit_code == 0
    assert "ok" in result.output


def test_lifecycle_remove_missing(runner, cli):
    result = invoke(runner, cli, ["lifecycle", "remove", "GHOST"])
    assert result.exit_code == 0
    assert "warn" in result.output


def test_lifecycle_list_empty(runner, cli):
    result = invoke(runner, cli, ["lifecycle", "list"])
    assert result.exit_code == 0
    assert "No lifecycle" in result.output


def test_lifecycle_list_filtered(runner, cli, store_path):
    set_lifecycle(store_path, "A", "active")
    set_lifecycle(store_path, "B", "draft")
    result = invoke(runner, cli, ["lifecycle", "list", "--state", "active"])
    assert result.exit_code == 0
    assert "A" in result.output
    assert "B" not in result.output


def test_lifecycle_list_all(runner, cli, store_path):
    set_lifecycle(store_path, "X", "retired")
    set_lifecycle(store_path, "Y", "active")
    result = invoke(runner, cli, ["lifecycle", "list"])
    assert result.exit_code == 0
    assert "X" in result.output
    assert "Y" in result.output
