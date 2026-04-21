"""Tests for envchain.env_rating."""

from __future__ import annotations

import pytest

from envchain.env_rating import (
    RatingResult,
    average_rating,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)


@pytest.fixture()
def store(tmp_path):
    return tmp_path


def test_set_and_get_rating(store):
    result = set_rating(store, "API_KEY", 4)
    assert isinstance(result, RatingResult)
    assert result.ok
    assert result.rating == 4
    assert get_rating(store, "API_KEY") == 4


def test_get_missing_rating_returns_none(store):
    assert get_rating(store, "MISSING") is None


def test_invalid_rating_raises(store):
    with pytest.raises(ValueError):
        set_rating(store, "KEY", 0)
    with pytest.raises(ValueError):
        set_rating(store, "KEY", 6)


def test_overwrite_rating(store):
    set_rating(store, "DB_PASS", 2)
    set_rating(store, "DB_PASS", 5)
    assert get_rating(store, "DB_PASS") == 5


def test_remove_rating_returns_true(store):
    set_rating(store, "TOKEN", 3)
    assert remove_rating(store, "TOKEN") is True
    assert get_rating(store, "TOKEN") is None


def test_remove_missing_rating_returns_false(store):
    assert remove_rating(store, "GHOST") is False


def test_list_ratings_empty(store):
    assert list_ratings(store) == {}


def test_list_ratings_multiple(store):
    set_rating(store, "A", 1)
    set_rating(store, "B", 5)
    result = list_ratings(store)
    assert result == {"A": 1, "B": 5}


def test_average_rating_none_when_empty(store):
    assert average_rating(store) is None


def test_average_rating_single(store):
    set_rating(store, "X", 4)
    assert average_rating(store) == pytest.approx(4.0)


def test_average_rating_multiple(store):
    set_rating(store, "A", 2)
    set_rating(store, "B", 4)
    assert average_rating(store) == pytest.approx(3.0)


def test_repr_contains_stars(store):
    result = set_rating(store, "KEY", 3)
    r = repr(result)
    assert "★★★" in r
    assert "☆☆" in r
