import pytest
import os
from envchain.store import set_variable
from envchain.lint import lint_store, LintIssue, _check_key, _check_value

PASS = "testpass"


@pytest.fixture
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_lint_empty_store_no_issues(store):
    issues = lint_store(store, PASS)
    assert issues == []


def test_lint_valid_key_no_issues(store):
    set_variable(store, "MY_VAR", "hello", PASS)
    issues = lint_store(store, PASS)
    assert all(i.key != "MY_VAR" or i.level != "error" for i in issues)


def test_lint_lowercase_key_warns(store):
    set_variable(store, "my_var", "value", PASS)
    issues = lint_store(store, PASS)
    keys_with_warnings = [i for i in issues if i.key == "my_var" and i.level == "warning"]
    assert len(keys_with_warnings) >= 1


def test_lint_mixed_case_key_warns(store):
    set_variable(store, "MyVar", "value", PASS)
    issues = lint_store(store, PASS)
    warnings = [i for i in issues if i.key == "MyVar" and "uppercase" in i.message]
    assert len(warnings) == 1


def test_lint_empty_value_warns(store):
    set_variable(store, "EMPTY_VAR", "", PASS)
    issues = lint_store(store, PASS)
    value_issues = [i for i in issues if i.key == "EMPTY_VAR" and i.level == "warning"]
    assert len(value_issues) >= 1


def test_check_key_invalid_chars():
    issues = _check_key("MY-VAR")
    assert any(i.level == "error" for i in issues)


def test_check_key_starts_with_underscore():
    issues = _check_key("_PRIVATE")
    assert any("underscore" in i.message for i in issues)


def test_check_value_long_value():
    issues = _check_value("KEY", "x" * 5000)
    assert any("4096" in i.message for i in issues)


def test_lint_multiple_keys(store):
    set_variable(store, "GOOD_KEY", "val", PASS)
    set_variable(store, "bad_key", "val", PASS)
    issues = lint_store(store, PASS)
    bad_issues = [i for i in issues if i.key == "bad_key"]
    assert len(bad_issues) >= 1
