"""Lock/unlock store access with a session timeout."""
import json
import time
from pathlib import Path

SESSION_FILE = ".envchain_session"


def _session_path(store_path: str) -> Path:
    return Path(store_path).parent / SESSION_FILE


def lock_store(store_path: str) -> None:
    """Remove session file, effectively locking the store."""
    p = _session_path(store_path)
    if p.exists():
        p.unlink()


def unlock_store(store_path: str, passphrase: str, ttl_seconds: int = 300) -> None:
    """Write a session file with expiry so repeated commands skip passphrase prompt."""
    p = _session_path(store_path)
    session = {
        "passphrase": passphrase,
        "expires_at": time.time() + ttl_seconds,
    }
    p.write_text(json.dumps(session))
    p.chmod(0o600)


def get_unlocked_passphrase(store_path: str) -> str | None:
    """Return cached passphrase if session is still valid, else None."""
    p = _session_path(store_path)
    if not p.exists():
        return None
    try:
        session = json.loads(p.read_text())
        if time.time() < session["expires_at"]:
            return session["passphrase"]
        p.unlink()
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def is_locked(store_path: str) -> bool:
    return get_unlocked_passphrase(store_path) is None


def session_remaining(store_path: str) -> float:
    """Return seconds remaining in current session, or 0."""
    p = _session_path(store_path)
    if not p.exists():
        return 0.0
    try:
        session = json.loads(p.read_text())
        remaining = session["expires_at"] - time.time()
        return max(0.0, remaining)
    except (json.JSONDecodeError, KeyError):
        return 0.0
