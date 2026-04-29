"""CLI commands for variable attestation."""
from __future__ import annotations

import click
from pathlib import Path
from typing import Callable

from .env_attestation import attest_variable, get_attestation, remove_attestation, list_attestations


def register_attestation_commands(cli: click.Group, get_store: Callable[[], Path]) -> None:
    @cli.group("attest")
    def cmd_attest():
        """Manage variable attestations."""

    @cmd_attest.command("set")
    @click.argument("key")
    @click.argument("attested_by")
    @click.option("--note", default=None, help="Optional attestation note.")
    def cmd_attest_set(key: str, attested_by: str, note: str | None):
        """Attest a variable as verified by ATTESTED_BY."""
        store = get_store()
        result = attest_variable(store, key, attested_by, note=note)
        if result.ok:
            click.echo(f"Attested '{key}' by '{attested_by}'.")
        else:
            click.echo(f"Error: {result.error}", err=True)
            raise SystemExit(1)

    @cmd_attest.command("get")
    @click.argument("key")
    def cmd_attest_get(key: str):
        """Show attestation info for KEY."""
        store = get_store()
        result = get_attestation(store, key)
        if result is None:
            click.echo(f"No attestation found for '{key}'.")
        else:
            click.echo(f"Key:          {result.key}")
            click.echo(f"Attested by:  {result.attested_by}")
            import datetime
            ts = datetime.datetime.fromtimestamp(result.attested_at).isoformat()
            click.echo(f"Attested at:  {ts}")
            if result.note:
                click.echo(f"Note:         {result.note}")

    @cmd_attest.command("remove")
    @click.argument("key")
    def cmd_attest_remove(key: str):
        """Remove attestation for KEY."""
        store = get_store()
        removed = remove_attestation(store, key)
        if removed:
            click.echo(f"Attestation for '{key}' removed.")
        else:
            click.echo(f"No attestation found for '{key}'.")

    @cmd_attest.command("list")
    def cmd_attest_list():
        """List all attested variables."""
        store = get_store()
        entries = list_attestations(store)
        if not entries:
            click.echo("No attestations recorded.")
        else:
            for e in entries:
                note_str = f" ({e.note})" if e.note else ""
                click.echo(f"{e.key}: attested by {e.attested_by!r}{note_str}")
