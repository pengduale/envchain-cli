"""CLI tests for envchain lineage commands."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
import click

from envchain.cli_env_lineage import register_lineage_commands
from envchain.env_lineage import record_lineage


@pytest.fixture
def store_path(tmp_path):
    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    def root():
        pass

    def get_store(ctx):
        return str(store_path)

    register_lineage_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_lineage_list_empty(runner, cli):
    result = invoke(runner, cli, ["lineage", "list"])
    assert result.exit_code == 0
    assert "No lineage records" in result.output


def test_lineage_record_and_show(runner, cli, store_path):
    result = invoke(runner, cli, [
        "lineage", "record", "API_KEY",
        "--source-key", "API_KEY",
        "--source-profile", "dev",
        "--operation", "copy",
    ])
    assert result.exit_code == 0
    assert "Recorded lineage" in result.output

    result = invoke(runner, cli, ["lineage", "show", "API_KEY"])
    assert result.exit_code == 0
    assert "copy" in result.output
    assert "dev" in result.output


def test_lineage_show_missing_key(runner, cli):
    result = invoke(runner, cli, ["lineage", "show", "MISSING"])
    assert result.exit_code == 0
    assert "No lineage" in result.output


def test_lineage_record_with_note(runner, cli):
    result = invoke(runner, cli, [
        "lineage", "record", "DB_URL",
        "--source-key", "DB_URL",
        "--source-profile", "staging",
        "--operation", "promote",
        "--note", "promoted for release",
    ])
    assert result.exit_code == 0
    show = invoke(runner, cli, ["lineage", "show", "DB_URL"])
    assert "promoted for release" in show.output


def test_lineage_clear(runner, cli, store_path):
    record_lineage(store_path, "SECRET", "SECRET", "prod", "manual")
    result = invoke(runner, cli, ["lineage", "clear", "SECRET"])
    assert result.exit_code == 0
    assert "cleared" in result.output


def test_lineage_clear_missing(runner, cli):
    result = invoke(runner, cli, ["lineage", "clear", "GHOST"])
    assert result.exit_code == 0
    assert "No lineage" in result.output


def test_lineage_list_shows_keys(runner, cli, store_path):
    record_lineage(store_path, "FOO", "FOO", "dev", "import")
    record_lineage(store_path, "BAR", "BAR", "dev", "clone")
    result = invoke(runner, cli, ["lineage", "list"])
    assert "FOO" in result.output
    assert "BAR" in result.output
