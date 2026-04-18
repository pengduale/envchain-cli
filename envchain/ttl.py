"""TTL (time-to-live) support for environment variables."""
import json
import time
from pathlib import Path


def _ttl_path(store_path: Path) -> Path:
    return store_path.parent / (store_path.stem + ".ttl.json")


def _load_ttl(store_path: Path) -> dict:
    p = _ttl_path(store_path)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_ttl(store_path: Path, data: dict) -> None:
    _ttl_path(store_path).write_text(json.dumps(data, indent=2))


def set_ttl(store_path: Path, key: str, seconds: int) -> None:
    """Set expiry for a key (epoch seconds from now)."""
    data = _load_ttl(store_path)
    data[key] = time.time() + seconds
    _save_ttl(store_path, data)


def clear_ttl(store_path: Path, key: str) -> None:
    data = _load_ttl(store_path)
    data.pop(key, None)
    _save_ttl(store_path, data)


def get_expiry(store_path: Path, key: str) -> float | None:
    return _load_ttl(store_path).get(key)


def is_expired(store_path: Path, key: str) -> bool:
    expiry = get_expiry(store_path, key)
    if expiry is None:
        return False
    return time.time() > expiry


def purge_expired(store_path: Path) -> list[str]:
    """Remove expired entries from TTL index; return list of expired keys."""
    data = _load_ttl(store_path)
    now = time.time()
    expired = [k for k, exp in data.items() if now > exp]
    for k in expired:
        del data[k]
    if expired:
        _save_ttl(store_path, data)
    return expired
