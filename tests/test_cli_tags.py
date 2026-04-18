"""Tests for CLI tag commands."""
import json
import pytest
from click.testing import CliRunner
from envchain.cli_tags import register_tag_commands
from envchain.tags import tag_variable
import click


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "store.json"
    p.write_text(json.dumps({}))
    return str(p)


@pytest.fixture
def invoke(runner, store_path):
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.ensure_object(dict)

    def get_store(ctx):
        return store_path

    register_tag_commands(cli, get_store)

    def _invoke(*args):
        return runner.invoke(cli, list(args))

    return _invoke


def test_tag_add(invoke, store_path):
    result = invoke("tag", "add", "MY_KEY", "production")
    assert result.exit_code == 0
    assert "Tagged" in result.output


def test_tag_remove(invoke, store_path):
    tag_variable(store_path, "MY_KEY", "production")
    result = invoke("tag", "remove", "MY_KEY", "production")
    assert result.exit_code == 0
    assert "Removed" in result.output


def test_tag_list_shows_tags(invoke, store_path):
    tag_variable(store_path, "MY_KEY", "staging")
    result = invoke("tag", "list", "MY_KEY")
    assert "staging" in result.output


def test_tag_list_empty(invoke):
    result = invoke("tag", "list", "MISSING_KEY")
    assert "No tags" in result.output


def test_tag_find(invoke, store_path):
    tag_variable(store_path, "DB_URL", "infra")
    result = invoke("tag", "find", "infra")
    assert "DB_URL" in result.output


def test_tag_all(invoke, store_path):
    tag_variable(store_path, "X", "foo")
    result = invoke("tag", "all")
    assert "X" in result.output
    assert "foo" in result.output
