"""CLI tests for the signature feature."""
from __future__ import annotations

import pytest
from click.testing import CliRunner
import click

from envchain.cli_env_signature import register_signature_commands

SECRET = "cli-test-secret"


@pytest.fixture()
def store_path(tmp_path):
    p = tmp_path / "store.json"
    p.write_text("{}")
    return p


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

    register_signature_commands(root, get_store)
    return root


def invoke(runner, cli, *args, **kwargs):
    return runner.invoke(cli, list(args), catch_exceptions=False, **kwargs)


def test_sign_and_verify_success(runner, cli):
    r = invoke(runner, cli, "signature", "sign", "MY_KEY", "my_value", "--secret", SECRET)
    assert r.exit_code == 0
    assert "Signed" in r.output

    r2 = invoke(runner, cli, "signature", "verify", "MY_KEY", "my_value", "--secret", SECRET)
    assert r2.exit_code == 0
    assert "OK" in r2.output


def test_verify_wrong_value_exits_nonzero(runner, cli):
    invoke(runner, cli, "signature", "sign", "MY_KEY", "correct", "--secret", SECRET)
    r = invoke(runner, cli, "signature", "verify", "MY_KEY", "wrong", "--secret", SECRET)
    assert r.exit_code != 0
    assert "FAIL" in r.output


def test_verify_missing_key_exits_nonzero(runner, cli):
    r = invoke(runner, cli, "signature", "verify", "GHOST", "val", "--secret", SECRET)
    assert r.exit_code != 0


def test_remove_signature(runner, cli):
    invoke(runner, cli, "signature", "sign", "DEL_KEY", "v", "--secret", SECRET)
    r = invoke(runner, cli, "signature", "remove", "DEL_KEY")
    assert r.exit_code == 0
    assert "removed" in r.output


def test_remove_missing_signature(runner, cli):
    r = invoke(runner, cli, "signature", "remove", "GHOST")
    assert r.exit_code == 0
    assert "No signature" in r.output


def test_list_empty(runner, cli):
    r = invoke(runner, cli, "signature", "list")
    assert r.exit_code == 0
    assert "No signatures" in r.output


def test_list_shows_keys(runner, cli):
    invoke(runner, cli, "signature", "sign", "A", "1", "--secret", SECRET)
    invoke(runner, cli, "signature", "sign", "B", "2", "--secret", SECRET)
    r = invoke(runner, cli, "signature", "list")
    assert r.exit_code == 0
    assert "A" in r.output
    assert "B" in r.output
