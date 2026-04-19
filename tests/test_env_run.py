"""Tests for envchain.env_run."""
import os
import pytest

from envchain.store import set_variable
from envchain.env_run import build_env, run_command


PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_build_env_contains_os_environ(store):
    set_variable(store, "MY_VAR", "hello", PASS)
    env = build_env(store, PASS)
    # Should still have PATH etc.
    assert "PATH" in env


def test_build_env_injects_stored_vars(store):
    set_variable(store, "MY_SECRET", "s3cr3t", PASS)
    env = build_env(store, PASS)
    assert env["MY_SECRET"] == "s3cr3t"


def test_build_env_extra_overrides(store):
    set_variable(store, "FOO", "from_store", PASS)
    env = build_env(store, PASS, extra={"FOO": "overridden"})
    assert env["FOO"] == "overridden"


def test_build_env_empty_store(store):
    env = build_env(store, PASS)
    assert isinstance(env, dict)
    assert "PATH" in env


def test_run_command_exit_code(store):
    set_variable(store, "RUN_VAR", "42", PASS)
    code = run_command(["sh", "-c", "exit 0"], store, PASS)
    assert code == 0


def test_run_command_nonzero_exit(store):
    code = run_command(["sh", "-c", "exit 7"], store, PASS)
    assert code == 7


def test_run_command_env_visible_to_subprocess(store, tmp_path):
    set_variable(store, "INJECTED_VAR", "envchain_works", PASS)
    out_file = tmp_path / "out.txt"
    run_command(
        ["sh", "-c", f"echo $INJECTED_VAR > {out_file}"],
        store,
        PASS,
    )
    assert out_file.read_text().strip() == "envchain_works"
