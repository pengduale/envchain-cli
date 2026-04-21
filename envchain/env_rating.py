"""Per-key quality/confidence rating (1-5 stars) for stored variables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _rating_path(store_path: Path) -> Path:
    return store_path / ".ratings.json"


def _load_ratings(store_path: Path) -> dict:
    p = _rating_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ratings(store_path: Path, data: dict) -> None:
    _rating_path(store_path).write_text(json.dumps(data, indent=2))


@dataclass
class RatingResult:
    key: str
    rating: int
    ok: bool
    message: str

    def __repr__(self) -> str:
        stars = "★" * self.rating + "☆" * (5 - self.rating)
        return f"RatingResult({self.key!r}, {stars}, ok={self.ok})"


VALID_RATINGS = frozenset(range(1, 6))


def set_rating(store_path: Path, key: str, rating: int) -> RatingResult:
    """Assign a 1-5 star rating to *key*."""
    if rating not in VALID_RATINGS:
        raise ValueError(f"Rating must be between 1 and 5, got {rating}")
    data = _load_ratings(store_path)
    data[key] = rating
    _save_ratings(store_path, data)
    return RatingResult(key=key, rating=rating, ok=True, message="Rating set.")


def get_rating(store_path: Path, key: str) -> Optional[int]:
    """Return the rating for *key*, or None if not set."""
    return _load_ratings(store_path).get(key)


def remove_rating(store_path: Path, key: str) -> bool:
    """Remove the rating for *key*. Returns True if it existed."""
    data = _load_ratings(store_path)
    if key not in data:
        return False
    del data[key]
    _save_ratings(store_path, data)
    return True


def list_ratings(store_path: Path) -> dict[str, int]:
    """Return all key→rating mappings."""
    return dict(_load_ratings(store_path))


def average_rating(store_path: Path) -> Optional[float]:
    """Return the mean rating across all rated keys, or None if none exist."""
    data = _load_ratings(store_path)
    if not data:
        return None
    return sum(data.values()) / len(data)
