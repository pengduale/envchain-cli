"""Tests for passphrase rotation."""

from __future__ import annotations

import json
import pytest
from click.testing import CliRunner
from pathlib import Path

from envchain.rotate import rotate_passphrase, rotate_single
from envchain.store import set_variable, get_variable
from envchain.cli_rotate import cmd_rotate, cmd_rotate_one


OLD_PASS = "old-secret"
NEW_PASS = "new-secret"


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    p = tmp_path / ".envchain.json"
    set_variable(p, "FOO", "bar", OLD_PASS)
    set_variable(p, "BAZ", "qux", OLD_PASS)
    return p


def test_rotate_passphrase_returns_count(store: Path) -> None:
    count = rotate_passphrase(store, OLD_PASS, NEW_PASS)
    assert count == 2


def test_rotate_passphrase_values_readable_with_new_pass(store: Path) -> None:
    rotate_passphrase(store, OLD_PASS, NEW_PASS)
    assert get_variable(store, "FOO", NEW_PASS) == "bar"
    assert get_variable(store, "BAZ", NEW_PASS) == "qux"


def test_rotate_passphrase_old_pass_invalid_after_rotation(store: Path) -> None:
    from cryptography.fernet import InvalidToken
    rotate_passphrase(store, OLD_PASS, NEW_PASS)
    with pytest.raises(InvalidToken):
        get_variable(store, "FOO", OLD_PASS)


def test_rotate_empty_store_raises(tmp_path: Path) -> None:
    p = tmp_path / ".envchain.json"
    p.write_text(json.dumps({}))
    with pytest.raises(ValueError, match="empty"):
        rotate_passphrase(p, OLD_PASS, NEW_PASS)


def test_rotate_single(store: Path) -> None:
    rotate_single(store, "FOO", OLD_PASS, NEW_PASS)
    assert get_variable(store, "FOO", NEW_PASS) == "bar"
    # BAZ still encrypted with old pass
    assert get_variable(store, "BAZ", OLD_PASS) == "qux"


def test_rotate_single_missing_key_raises(store: Path) -> None:
    with pytest.raises(KeyError):
        rotate_single(store, "MISSING", OLD_PASS, NEW_PASS)


def test_cmd_rotate_cli(store: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cmd_rotate,
        ["--store", str(store), "--old-passphrase", OLD_PASS, "--new-passphrase", NEW_PASS],
    )
    assert result.exit_code == 0
    assert "2 variable(s)" in result.output


def test_cmd_rotate_one_cli(store: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cmd_rotate_one,
        ["FOO", "--store", str(store), "--old-passphrase", OLD_PASS, "--new-passphrase", NEW_PASS],
    )
    assert result.exit_code == 0
    assert "FOO" in result.output
