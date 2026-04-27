"""CLI tests for the readonly command group."""

from __future__ import annotations

import pytest
from pathlib import Path
from click.testing import CliRunner
import click

from envchain.cli_env_readonly import register_readonly_commands, cmd_readonly
from envchain.env_readonly import set_readonly


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / ".envchain.json"
    p.write_text("{}")
    return p


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)
        ctx.obj["store"] = store_path

    def get_store(ctx):
        return ctx.obj["store"]

    register_readonly_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_readonly_set(runner, cli, store_path):
    result = invoke(runner, cli, "readonly", "set", "API_KEY")
    assert result.exit_code == 0
    assert "locked" in result.output


def test_readonly_get_locked(runner, cli, store_path):
    set_readonly(store_path, "API_KEY", locked=True)
    result = invoke(runner, cli, "readonly", "get", "API_KEY")
    assert result.exit_code == 0
    assert "read-only" in result.output


def test_readonly_get_writable(runner, cli, store_path):
    result = invoke(runner, cli, "readonly", "get", "FREE_KEY")
    assert result.exit_code == 0
    assert "writable" in result.output


def test_readonly_remove(runner, cli, store_path):
    set_readonly(store_path, "SECRET", locked=True)
    result = invoke(runner, cli, "readonly", "remove", "SECRET")
    assert result.exit_code == 0
    assert "unlocked" in result.output


def test_readonly_remove_missing(runner, cli, store_path):
    result = runner.invoke(cli, ["readonly", "remove", "GHOST"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "error" in result.output


def test_readonly_list_empty(runner, cli, store_path):
    result = invoke(runner, cli, "readonly", "list")
    assert result.exit_code == 0
    assert "No read-only" in result.output


def test_readonly_list_shows_keys(runner, cli, store_path):
    set_readonly(store_path, "KEY_X")
    set_readonly(store_path, "KEY_Y")
    result = invoke(runner, cli, "readonly", "list")
    assert result.exit_code == 0
    assert "KEY_X" in result.output
    assert "KEY_Y" in result.output
