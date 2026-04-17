"""Export and import environment variables to/from shell-compatible formats."""

from __future__ import annotations

import shlex
from typing import Dict, Optional


def export_to_shell(variables: Dict[str, str], shell: str = "bash") -> str:
    """Render a dict of env vars as shell export statements."""
    lines = []
    for key, value in sorted(variables.items()):
        safe_value = shlex.quote(value)
        if shell == "fish":
            lines.append(f"set -x {key} {safe_value}")
        else:
            lines.append(f"export {key}={safe_value}")
    return "\n".join(lines)


def export_to_dotenv(variables: Dict[str, str]) -> str:
    """Render a dict of env vars in .env file format."""
    lines = []
    for key, value in sorted(variables.items()):
        escaped = value.replace('"', '\\"')
        lines.append(f'{key}="{escaped}"')
    return "\n".join(lines)


def parse_dotenv(content: str) -> Dict[str, str]:
    """Parse a .env file content into a dict, ignoring comments and blanks."""
    result: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        raw_value = raw_value.strip()
        if len(raw_value) >= 2 and raw_value[0] in ('"', "'") and raw_value[-1] == raw_value[0]:
            raw_value = raw_value[1:-1]
        result[key] = raw_value
    return result
