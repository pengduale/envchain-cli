"""Template rendering: substitute env vars from store into template strings."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Optional

from envchain.store import get_variable, list_keys

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


def render_string(template: str, store_path: Path, passphrase: str) -> str:
    """Replace {{VAR}} placeholders with decrypted values from the store."""
    missing: list[str] = []

    def _replace(match: re.Match) -> str:
        key = match.group(1)
        value = get_variable(store_path, passphrase, key)
        if value is None:
            missing.append(key)
            return match.group(0)
        return value

    result = _PLACEHOLDER.sub(_replace, template)
    if missing:
        raise KeyError(f"Missing variables in store: {', '.join(missing)}")
    return result


def render_file(
    template_path: Path,
    store_path: Path,
    passphrase: str,
    output_path: Optional[Path] = None,
) -> str:
    """Render a template file. Writes to output_path if given; always returns rendered text."""
    template = template_path.read_text()
    rendered = render_string(template, store_path, passphrase)
    if output_path:
        output_path.write_text(rendered)
    return rendered


def list_placeholders(template: str) -> list[str]:
    """Return unique placeholder names found in a template string."""
    return list(dict.fromkeys(m.group(1) for m in _PLACEHOLDER.finditer(template)))
