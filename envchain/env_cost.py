"""Track cost/billing metadata for environment variables (e.g. API keys with usage costs)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

VALID_CURRENCIES = {"USD", "EUR", "GBP", "JPY", "CAD", "AUD"}


def _cost_path(store_path: Path) -> Path:
    return store_path.parent / ".envchain_cost.json"


def _load_costs(store_path: Path) -> dict:
    p = _cost_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_costs(store_path: Path, data: dict) -> None:
    _cost_path(store_path).write_text(json.dumps(data, indent=2))


class CostResult:
    def __init__(self, key: str, amount: float, currency: str, note: Optional[str], ok: bool, error: Optional[str] = None):
        self.key = key
        self.amount = amount
        self.currency = currency
        self.note = note
        self.ok = ok
        self.error = error

    def __repr__(self) -> str:
        if not self.ok:
            return f"CostResult(key={self.key!r}, error={self.error!r})"
        return f"CostResult(key={self.key!r}, amount={self.amount}, currency={self.currency!r})"


def set_cost(store_path: Path, key: str, amount: float, currency: str = "USD", note: Optional[str] = None) -> CostResult:
    if currency not in VALID_CURRENCIES:
        return CostResult(key, amount, currency, note, ok=False, error=f"Invalid currency '{currency}'. Choose from {sorted(VALID_CURRENCIES)}.")
    if amount < 0:
        return CostResult(key, amount, currency, note, ok=False, error="Amount must be non-negative.")
    data = _load_costs(store_path)
    data[key] = {"amount": amount, "currency": currency, "note": note}
    _save_costs(store_path, data)
    return CostResult(key, amount, currency, note, ok=True)


def get_cost(store_path: Path, key: str) -> Optional[CostResult]:
    data = _load_costs(store_path)
    if key not in data:
        return None
    entry = data[key]
    return CostResult(key, entry["amount"], entry["currency"], entry.get("note"), ok=True)


def remove_cost(store_path: Path, key: str) -> bool:
    data = _load_costs(store_path)
    if key not in data:
        return False
    del data[key]
    _save_costs(store_path, data)
    return True


def list_costs(store_path: Path) -> list[CostResult]:
    data = _load_costs(store_path)
    return [
        CostResult(k, v["amount"], v["currency"], v.get("note"), ok=True)
        for k, v in data.items()
    ]
