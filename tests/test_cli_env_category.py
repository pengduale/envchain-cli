"""Tests for CLI category commands."""
import pytest
from click.testing import CliRunner
import click
from envchain.cli_env_category import register_category_commands


@pytest.fixture
def store_path(tmp_path):
    return str(tmp_path)


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

    register_category_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_set_and_get(runner, cli):
    r = invoke(runner, cli, ["category", "set", "DB_URL", "database"])
    assert r.exit_code == 0
    assert "database" in r.output
    r = invoke(runner, cli, ["category", "get", "DB_URL"])
    assert r.exit_code == 0
    assert "database" in r.output


def test_get_missing(runner, cli):
    r = runner.invoke(cli, ["category", "get", "MISSING"])
    assert r.exit_code != 0


def test_remove(runner, cli):
    invoke(runner, cli, ["category", "set", "TOKEN", "auth"])
    r = invoke(runner, cli, ["category", "remove", "TOKEN"])
    assert r.exit_code == 0
    r = runner.invoke(cli, ["category", "get", "TOKEN"])
    assert r.exit_code != 0


def test_list_empty(runner, cli):
    r = invoke(runner, cli, ["category", "list"])
    assert r.exit_code == 0
    assert "No categories" in r.output


def test_list_grouped(runner, cli):
    invoke(runner, cli, ["category", "set", "DB_URL", "database"])
    invoke(runner, cli, ["category", "set", "API_KEY", "auth"])
    r = invoke(runner, cli, ["category", "list", "--group"])
    assert r.exit_code == 0
    assert "[auth]" in r.output
    assert "[database]" in r.output
    assert "DB_URL" in r.output
