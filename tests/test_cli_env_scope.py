import pytest
from click.testing import CliRunner
import click
from envchain.cli_env_scope import register_scope_commands
from envchain.env_scope import set_scope


@pytest.fixture
def store_path(tmp_path):
    return str(tmp_path)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli(store_path):
    @click.group()
    def root():
        pass

    def get_store(ctx):
        return store_path, "passphrase"

    register_scope_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_scope_set(runner, cli):
    result = invoke(runner, cli, ["scope", "set", "ci", "API_KEY", "SECRET"])
    assert result.exit_code == 0
    assert "ci" in result.output
    assert "API_KEY" in result.output


def test_scope_get(runner, cli, store_path):
    set_scope(store_path, "ci", ["FOO", "BAR"])
    result = invoke(runner, cli, ["scope", "get", "ci"])
    assert "FOO" in result.output
    assert "BAR" in result.output


def test_scope_get_missing(runner, cli):
    result = runner.invoke(cli, ["scope", "get", "nope"])
    assert result.exit_code != 0 or "not found" in result.output


def test_scope_remove(runner, cli, store_path):
    set_scope(store_path, "dev", ["X"])
    result = invoke(runner, cli, ["scope", "remove", "dev"])
    assert "removed" in result.output


def test_scope_list_empty(runner, cli):
    result = invoke(runner, cli, ["scope", "list"])
    assert "No scopes" in result.output


def test_scope_list_shows_scopes(runner, cli, store_path):
    set_scope(store_path, "prod", ["A", "B"])
    result = invoke(runner, cli, ["scope", "list"])
    assert "prod" in result.output
