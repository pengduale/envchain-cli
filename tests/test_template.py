"""Tests for envchain.template."""
import pytest
from pathlib import Path
from envchain.template import render_string, render_file, list_placeholders
from envchain.store import set_variable


@pytest.fixture
def store(tmp_path):
    passphrase = "testpass"
    store_path = tmp_path / "store.json"
    set_variable(store_path, passphrase, "HOST", "localhost")
    set_variable(store_path, passphrase, "PORT", "5432")
    set_variable(store_path, passphrase, "DB_PASS", "s3cr3t")
    return store_path, passphrase


def test_render_simple(store):
    store_path, passphrase = store
    result = render_string("Connect to {{ HOST }}:{{ PORT }}", store_path, passphrase)
    assert result == "Connect to localhost:5432"


def test_render_no_placeholders(store):
    store_path, passphrase = store
    result = render_string("No vars here.", store_path, passphrase)
    assert result == "No vars here."


def test_render_missing_key_raises(store):
    store_path, passphrase = store
    with pytest.raises(KeyError, match="MISSING"):
        render_string("value={{ MISSING }}", store_path, passphrase)


def test_render_repeated_placeholder(store):
    store_path, passphrase = store
    result = render_string("{{HOST}} and {{HOST}}", store_path, passphrase)
    assert result == "localhost and localhost"


def test_render_file_returns_string(store, tmp_path):
    store_path, passphrase = store
    tpl = tmp_path / "config.tpl"
    tpl.write_text("host={{HOST}}\nport={{PORT}}")
    result = render_file(tpl, store_path, passphrase)
    assert "localhost" in result
    assert "5432" in result


def test_render_file_writes_output(store, tmp_path):
    store_path, passphrase = store
    tpl = tmp_path / "config.tpl"
    tpl.write_text("pass={{DB_PASS}}")
    out = tmp_path / "config.out"
    render_file(tpl, store_path, passphrase, output_path=out)
    assert out.exists()
    assert out.read_text() == "pass=s3cr3t"


def test_list_placeholders():
    text = "{{FOO}} and {{BAR}} and {{FOO}}"
    result = list_placeholders(text)
    assert result == ["FOO", "BAR"]


def test_list_placeholders_empty():
    assert list_placeholders("no vars") == []
