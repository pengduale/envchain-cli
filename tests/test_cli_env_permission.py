import pytest
from click.testing import CliRunner
import click
from envchain.cli_env_permission import register_permission_commands


@pytest.fixture
def store_path(tmp_path):
    return str(tmp_path / "store.json")


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

    register_permission_commands(root, get_store)
    return root


def invoke(runner, cli, args):
    return runner.invoke(cli, args, catch_exceptions=False)


def test_permission_set_and_get(runner, cli):
    result = invoke(runner, cli, ["permission", "set", "API_KEY", "read", "write"])
    assert result.exit_code == 0
    assert "API_KEY" in result.output
    assert "read" in result.output


def test_permission_get_missing(runner, cli):
    result = invoke(runner, cli, ["permission", "get", "MISSING"])
    assert result.exit_code == 0
    assert "No restrictions" in result.output


def test_permission_set_invalid(runner, cli):
    result = runner.invoke(cli, ["permission", "set", "KEY", "execute"])
    assert result.exit_code != 0


def test_permission_remove(runner, cli):
    invoke(runner, cli, ["permission", "set", "DB_PASS", "read"])
    result = invoke(runner, cli, ["permission", "remove", "DB_PASS"])
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_permission_remove_missing(runner, cli):
    result = invoke(runner, cli, ["permission", "remove", "GHOST"])
    assert result.exit_code == 0
    assert "No permissions found" in result.output


def test_permission_check_allowed(runner, cli):
    invoke(runner, cli, ["permission", "set", "KEY", "read", "write"])
    result = invoke(runner, cli, ["permission", "check", "KEY", "read"])
    assert "allowed" in result.output


def test_permission_check_denied(runner, cli):
    invoke(runner, cli, ["permission", "set", "KEY", "read"])
    result = invoke(runner, cli, ["permission", "check", "KEY", "delete"])
    assert "denied" in result.output


def test_permission_list_empty(runner, cli):
    result = invoke(runner, cli, ["permission", "list"])
    assert "No permission restrictions" in result.output


def test_permission_list_shows_keys(runner, cli):
    invoke(runner, cli, ["permission", "set", "X", "read"])
    invoke(runner, cli, ["permission", "set", "Y", "write", "delete"])
    result = invoke(runner, cli, ["permission", "list"])
    assert "X" in result.output
    assert "Y" in result.output
