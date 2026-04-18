"""Tests for envchain.search."""

from __future__ import annotations

import pytest

from envchain.store import set_variable
from envchain.profile import set_profile_variable
from envchain.search import search_default, search_profile, search_all_profiles

PASS = "hunter2"


@pytest.fixture()
def store(tmp_path):
    return str(tmp_path / "store.json")


def test_search_default_exact(store):
    set_variable(store, "DB_HOST", "localhost", PASS)
    hits = search_default("DB_HOST", PASS, store)
    assert hits == [("DB_HOST", "localhost")]


def test_search_default_wildcard(store):
    set_variable(store, "DB_HOST", "localhost", PASS)
    set_variable(store, "DB_PORT", "5432", PASS)
    set_variable(store, "API_KEY", "secret", PASS)
    hits = search_default("DB_*", PASS, store)
    keys = [k for k, _ in hits]
    assert "DB_HOST" in keys
    assert "DB_PORT" in keys
    assert "API_KEY" not in keys


def test_search_default_no_match(store):
    set_variable(store, "FOO", "bar", PASS)
    hits = search_default("NOTHING_*", PASS, store)
    assert hits == []


def test_search_profile(store):
    set_profile_variable(store, "staging", "APP_ENV", "staging", PASS)
    set_profile_variable(store, "staging", "APP_DEBUG", "true", PASS)
    hits = search_profile("APP_*", PASS, store, "staging")
    keys = [k for k, _ in hits]
    assert "APP_ENV" in keys
    assert "APP_DEBUG" in keys


def test_search_all_profiles(store):
    set_variable(store, "SHARED_KEY", "val0", PASS)
    set_profile_variable(store, "prod", "SHARED_KEY", "val1", PASS)
    set_profile_variable(store, "dev", "OTHER", "val2", PASS)

    results = search_all_profiles("SHARED_*", PASS, store)
    assert "default" in results
    assert "prod" in results
    assert "dev" not in results


def test_search_all_profiles_no_match(store):
    set_variable(store, "FOO", "bar", PASS)
    results = search_all_profiles("ZZZNOMATCH", PASS, store)
    assert results == {}
