"""CLI tests for trust-level commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path

import click

from envchain.cli_env_trust import register_trust_commands
from envchain.env_trust import set_trust


@pytest.fixture
def store_path(tmp_path):
    return tmp_path / "store.json"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)
        ctx.obj["store"] = str(store_path)

    def get_store(ctx):
        return ctx.obj["store"]

    register_trust_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_trust_set_and_get(runner, cli, store_path):
    result = invoke(runner, cli, "trust", "set", "API_KEY", "high")
    assert result.exit_code == 0
    assert "ok" in result.output

    result = invoke(runner, cli, "trust", "get", "API_KEY")
    assert result.exit_code == 0
    assert "high" in result.output


def test_trust_get_missing(runner, cli):
    result = invoke(runner, cli, "trust", "get", "MISSING")
    assert result.exit_code == 0
    assert "No trust level" in result.output


def test_trust_remove_existing(runner, cli, store_path):
    set_trust(store_path, "TOKEN", "medium")
    result = invoke(runner, cli, "trust", "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_trust_remove_missing(runner, cli):
    result = invoke(runner, cli, "trust", "remove", "GHOST")
    assert result.exit_code == 0
    assert "No trust level found" in result.output


def test_trust_list_empty(runner, cli):
    result = invoke(runner, cli, "trust", "list")
    assert result.exit_code == 0
    assert "No trust levels" in result.output


def test_trust_list_shows_entries(runner, cli, store_path):
    set_trust(store_path, "DB_URL", "verified")
    set_trust(store_path, "SECRET", "low")
    result = invoke(runner, cli, "trust", "list")
    assert result.exit_code == 0
    assert "DB_URL" in result.output
    assert "verified" in result.output
    assert "SECRET" in result.output
    assert "low" in result.output
