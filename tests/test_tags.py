"""Tests for envchain.tags module."""
import json
import pytest
from pathlib import Path
from envchain.tags import tag_variable, untag_variable, get_tags, list_by_tag, all_tags


@pytest.fixture
def store(tmp_path):
    p = tmp_path / "store.json"
    p.write_text(json.dumps({}))
    return str(p)


def test_tag_variable_adds_tag(store):
    tag_variable(store, "DB_URL", "database")
    assert "database" in get_tags(store, "DB_URL")


def test_tag_variable_no_duplicates(store):
    tag_variable(store, "DB_URL", "database")
    tag_variable(store, "DB_URL", "database")
    assert get_tags(store, "DB_URL").count("database") == 1


def test_tag_multiple_tags(store):
    tag_variable(store, "API_KEY", "api")
    tag_variable(store, "API_KEY", "secret")
    tags = get_tags(store, "API_KEY")
    assert "api" in tags
    assert "secret" in tags


def test_untag_removes_tag(store):
    tag_variable(store, "DB_URL", "database")
    untag_variable(store, "DB_URL", "database")
    assert get_tags(store, "DB_URL") == []


def test_untag_nonexistent_tag_is_safe(store):
    untag_variable(store, "DB_URL", "ghost")
    assert get_tags(store, "DB_URL") == []


def test_list_by_tag_returns_correct_keys(store):
    tag_variable(store, "DB_URL", "database")
    tag_variable(store, "DB_PASS", "database")
    tag_variable(store, "API_KEY", "api")
    keys = list_by_tag(store, "database")
    assert set(keys) == {"DB_URL", "DB_PASS"}


def test_list_by_tag_no_match(store):
    assert list_by_tag(store, "nonexistent") == []


def test_all_tags_returns_full_mapping(store):
    tag_variable(store, "A", "x")
    tag_variable(store, "B", "y")
    mapping = all_tags(store)
    assert mapping["A"] == ["x"]
    assert mapping["B"] == ["y"]


def test_all_tags_empty_store(store):
    assert all_tags(store) == {}
