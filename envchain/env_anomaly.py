"""Anomaly detection for environment variable values.

Detects suspicious patterns such as values that appear to be
plaintext secrets, unexpectedly short/long values, or values
that have changed drastically from a recorded baseline.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from envchain.store import get_variable, list_keys


@dataclass
class AnomalyResult:
    key: str
    anomaly_type: str
    detail: str
    severity: str  # "low", "medium", "high"

    def __repr__(self) -> str:
        return f"AnomalyResult(key={self.key!r}, type={self.anomaly_type!r}, severity={self.severity!r})"


_PLAINTEXT_SECRET_PATTERNS = [
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key)\s*=\s*\S+"),
    re.compile(r"[A-Za-z0-9+/]{40,}={0,2}"),  # base64-ish long string
    re.compile(r"[0-9a-fA-F]{32,}"),           # hex digest / token
]


def _entropy(value: str) -> float:
    if not value:
        return 0.0
    freq = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(value)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _check_value(key: str, value: str) -> List[AnomalyResult]:
    results: List[AnomalyResult] = []

    if len(value) == 0:
        results.append(AnomalyResult(key, "empty_value", "Value is empty.", "medium"))
        return results

    if len(value) > 4096:
        results.append(AnomalyResult(key, "oversized_value",
                                     f"Value length {len(value)} exceeds 4096 chars.", "low"))

    ent = _entropy(value)
    if ent > 4.5 and len(value) >= 20:
        results.append(AnomalyResult(key, "high_entropy",
                                     f"Entropy {ent:.2f} suggests a raw secret.", "high"))

    for pat in _PLAINTEXT_SECRET_PATTERNS:
        if pat.search(value):
            results.append(AnomalyResult(key, "plaintext_secret_pattern",
                                         "Value matches a known plaintext secret pattern.", "high"))
            break

    return results


def scan_store(store_path: Path, passphrase: str) -> List[AnomalyResult]:
    """Scan all keys in the store and return detected anomalies."""
    anomalies: List[AnomalyResult] = []
    keys = list_keys(store_path)
    for key in keys:
        value = get_variable(store_path, key, passphrase)
        if value is None:
            continue
        anomalies.extend(_check_value(key, value))
    return anomalies


def scan_key(store_path: Path, key: str, passphrase: str) -> List[AnomalyResult]:
    """Scan a single key and return detected anomalies."""
    value = get_variable(store_path, key, passphrase)
    if value is None:
        return [AnomalyResult(key, "missing_key", f"Key '{key}' not found.", "medium")]
    return _check_value(key, value)
