"""CLI tests for envchain changelog commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
from pathlib import Path
import click

from envchain.cli_env_changelog import register_changelog_commands


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "store.json"
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
        ctx.obj["store_path"] = store_path

    def get_store(ctx):
        return ctx.obj["store_path"]

    register_changelog_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_add_changelog_entry(runner, cli):
    result = invoke(runner, cli, "changelog", "add", "API_KEY", "Initial setup")
    assert result.exit_code == 0
    assert "Added" in result.output
    assert "API_KEY" in result.output


def test_add_changelog_entry_with_author(runner, cli):
    result = invoke(runner, cli, "changelog", "add", "DB_PASS", "Rotated", "--author", "alice")
    assert result.exit_code == 0
    assert "alice" in result.output


def test_show_empty_changelog(runner, cli):
    result = invoke(runner, cli, "changelog", "show", "MISSING_KEY")
    assert result.exit_code == 0
    assert "No changelog entries" in result.output


def test_show_changelog_after_add(runner, cli):
    invoke(runner, cli, "changelog", "add", "TOKEN", "First")
    invoke(runner, cli, "changelog", "add", "TOKEN", "Second")
    result = invoke(runner, cli, "changelog", "show", "TOKEN")
    assert "First" in result.output
    assert "Second" in result.output


def test_clear_changelog(runner, cli):
    invoke(runner, cli, "changelog", "add", "SECRET", "some note")
    result = invoke(runner, cli, "changelog", "clear", "SECRET")
    assert "cleared" in result.output.lower()


def test_clear_missing_key(runner, cli):
    result = invoke(runner, cli, "changelog", "clear", "NOPE")
    assert "No changelog found" in result.output


def test_list_no_entries(runner, cli):
    result = invoke(runner, cli, "changelog", "list")
    assert "No changelog entries found" in result.output


def test_list_shows_keys(runner, cli):
    invoke(runner, cli, "changelog", "add", "KEY_A", "msg")
    invoke(runner, cli, "changelog", "add", "KEY_B", "msg")
    result = invoke(runner, cli, "changelog", "list")
    assert "KEY_A" in result.output
    assert "KEY_B" in result.output
