"""Attach plaintext notes/descriptions to stored environment variables."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


def _note_path(store_dir: str) -> Path:
    return Path(store_dir) / ".envchain_notes.json"


def _load_notes(store_dir: str) -> dict:
    p = _note_path(store_dir)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_notes(store_dir: str, notes: dict) -> None:
    _note_path(store_dir).write_text(json.dumps(notes, indent=2))


def set_note(store_dir: str, key: str, note: str) -> None:
    """Attach a note to a key."""
    notes = _load_notes(store_dir)
    notes[key] = note
    _save_notes(store_dir, notes)


def get_note(store_dir: str, key: str) -> Optional[str]:
    """Return the note for a key, or None."""
    return _load_notes(store_dir).get(key)


def remove_note(store_dir: str, key: str) -> bool:
    """Remove the note for a key. Returns True if it existed."""
    notes = _load_notes(store_dir)
    if key not in notes:
        return False
    del notes[key]
    _save_notes(store_dir, notes)
    return True


def list_notes(store_dir: str) -> dict[str, str]:
    """Return all key->note mappings."""
    return dict(_load_notes(store_dir))


def keys_with_notes(store_dir: str) -> list[str]:
    """Return keys that have notes attached."""
    return list(_load_notes(store_dir).keys())
