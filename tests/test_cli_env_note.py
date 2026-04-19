import pytest
from click.testing import CliRunner
import click
from envchain.env_note import set_note
from envchain.cli_env_note import register_note_commands


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
        ctx.obj["store_dir"] = store_path

    def get_store(ctx):
        return ctx.obj["store_dir"], None

    register_note_commands(root, get_store)
    return root


def invoke(runner, cli, *args):
    return runner.invoke(cli, list(args), catch_exceptions=False)


def test_note_set_and_get(runner, cli):
    result = invoke(runner, cli, "note", "set", "MY_KEY", "my description")
    assert result.exit_code == 0
    assert "Note set" in result.output

    result = invoke(runner, cli, "note", "get", "MY_KEY")
    assert result.exit_code == 0
    assert "my description" in result.output


def test_note_get_missing(runner, cli):
    result = runner.invoke(cli, ["note", "get", "MISSING"])
    assert result.exit_code != 0
    assert "No note" in result.output


def test_note_remove(runner, cli, store_path):
    set_note(store_path, "DEL_KEY", "to be removed")
    result = invoke(runner, cli, "note", "remove", "DEL_KEY")
    assert "removed" in result.output


def test_note_remove_missing(runner, cli):
    result = invoke(runner, cli, "note", "remove", "GHOST")
    assert "No note found" in result.output


def test_note_list_empty(runner, cli):
    result = invoke(runner, cli, "note", "list")
    assert "No notes" in result.output


def test_note_list_populated(runner, cli, store_path):
    set_note(store_path, "A", "alpha")
    set_note(store_path, "B", "beta")
    result = invoke(runner, cli, "note", "list")
    assert "A: alpha" in result.output
    assert "B: beta" in result.output
