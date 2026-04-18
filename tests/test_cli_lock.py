import pytest
from click.testing import CliRunner
import click
from envchain.cli_lock import register_lock_commands
from envchain.lock import unlock_store, is_locked


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "store" / ".envchain"
    p.parent.mkdir()
    p.write_text("{}")
    return str(p)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def invoke(runner, store_path):
    @click.group()
    @click.pass_context
    def cli(ctx):
        ctx.ensure_object(dict)

    def get_store(ctx):
        return store_path

    register_lock_commands(cli, get_store)

    def _invoke(args, input=None):
        return runner.invoke(cli, args, input=input, catch_exceptions=False)

    return _invoke


def test_lock_status_initially_locked(invoke):
    result = invoke(["lock-status"])
    assert "locked" in result.output


def test_unlock_then_status(invoke, store_path):
    result = invoke(["unlock", "--ttl", "60"], input="mysecret\n")
    assert "unlocked" in result.output
    result2 = invoke(["lock-status"])
    assert "unlocked" in result2.output


def test_lock_command(invoke, store_path):
    unlock_store(store_path, "pass", ttl_seconds=60)
    result = invoke(["lock"])
    assert "locked" in result.output
    assert is_locked(store_path)


def test_unlock_stores_passphrase(invoke, store_path):
    from envchain.lock import get_unlocked_passphrase
    invoke(["unlock", "--ttl", "300"], input="hunter2\n")
    assert get_unlocked_passphrase(store_path) == "hunter2"
