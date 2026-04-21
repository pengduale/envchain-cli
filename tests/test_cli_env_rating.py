"""CLI integration tests for the rating commands."""

from __future__ import annotations

import pytest
from click.testing import CliRunner
import click

from envchain.cli_env_rating import register_rating_commands
from envchain.env_rating import set_rating


@pytest.fixture()
def store_path(tmp_path):
    return tmp_path


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def cli(store_path):
    @click.group()
    @click.pass_context
    def root(ctx):
        ctx.ensure_object(dict)
        ctx.obj["store"] = store_path

    def get_store(ctx):
        return ctx.obj["store"]

    register_rating_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_rating_set(runner, cli):
    result = invoke(runner, cli, "rating", "set", "API_KEY", "4")
    assert result.exit_code == 0
    assert "★★★★" in result.output


def test_rating_get_after_set(runner, cli, store_path):
    set_rating(store_path, "DB_PASS", 5)
    result = invoke(runner, cli, "rating", "get", "DB_PASS")
    assert result.exit_code == 0
    assert "5/5" in result.output


def test_rating_get_missing(runner, cli):
    result = invoke(runner, cli, "rating", "get", "GHOST")
    assert result.exit_code == 0
    assert "No rating" in result.output


def test_rating_remove(runner, cli, store_path):
    set_rating(store_path, "TOKEN", 3)
    result = invoke(runner, cli, "rating", "remove", "TOKEN")
    assert result.exit_code == 0
    assert "removed" in result.output


def test_rating_remove_missing(runner, cli):
    result = invoke(runner, cli, "rating", "remove", "NONE")
    assert result.exit_code == 0
    assert "No rating found" in result.output


def test_rating_list_empty(runner, cli):
    result = invoke(runner, cli, "rating", "list")
    assert result.exit_code == 0
    assert "No ratings" in result.output


def test_rating_list_shows_average(runner, cli, store_path):
    set_rating(store_path, "A", 2)
    set_rating(store_path, "B", 4)
    result = invoke(runner, cli, "rating", "list")
    assert result.exit_code == 0
    assert "Average" in result.output
    assert "3.00" in result.output
