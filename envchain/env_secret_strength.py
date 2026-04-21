"""Evaluate the strength of stored secret values."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from envchain.store import list_variables, get_variable


STRENGTH_LEVELS = ("weak", "fair", "good", "strong")


@dataclass
class StrengthResult:
    key: str
    score: int          # 0-100
    level: str          # weak / fair / good / strong
    suggestions: List[str]

    def __repr__(self) -> str:
        return f"<StrengthResult key={self.key!r} level={self.level} score={self.score}>"


def _entropy(value: str) -> float:
    """Approximate Shannon entropy of *value*."""
    if not value:
        return 0.0
    freq = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _score_value(value: str) -> tuple[int, list[str]]:
    """Return (score 0-100, list-of-suggestions)."""
    score = 0
    tips: list[str] = []

    length = len(value)
    if length >= 32:
        score += 40
    elif length >= 16:
        score += 25
    elif length >= 8:
        score += 10
    else:
        tips.append("Use at least 16 characters for better strength.")

    if re.search(r"[A-Z]", value):
        score += 10
    else:
        tips.append("Add uppercase letters.")

    if re.search(r"[a-z]", value):
        score += 10
    else:
        tips.append("Add lowercase letters.")

    if re.search(r"\d", value):
        score += 10
    else:
        tips.append("Add digits.")

    if re.search(r"[^A-Za-z0-9]", value):
        score += 15
    else:
        tips.append("Add special characters (!@#$…).")

    entropy = _entropy(value)
    if entropy >= 4.0:
        score += 15
    elif entropy >= 3.0:
        score += 8
    else:
        tips.append("Increase character variety to raise entropy.")

    score = min(score, 100)
    return score, tips


def _level(score: int) -> str:
    if score >= 75:
        return "strong"
    if score >= 50:
        return "good"
    if score >= 25:
        return "fair"
    return "weak"


def check_strength(store_path: Path, passphrase: str, key: str) -> StrengthResult:
    """Evaluate strength of a single stored variable."""
    value = get_variable(store_path, passphrase, key)
    if value is None:
        raise KeyError(f"Key {key!r} not found in store.")
    score, tips = _score_value(value)
    return StrengthResult(key=key, score=score, level=_level(score), suggestions=tips)


def check_all_strength(store_path: Path, passphrase: str) -> List[StrengthResult]:
    """Evaluate strength of every variable in the store."""
    keys = list_variables(store_path)
    return [check_strength(store_path, passphrase, k) for k in keys]
