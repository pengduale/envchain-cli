"""CLI commands for env lineage tracking."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_lineage import (
    record_lineage,
    get_lineage,
    clear_lineage,
    list_lineage_keys,
    VALID_OPERATIONS,
)


def register_lineage_commands(cli: click.Group, get_store) -> None:
    @cli.group("lineage")
    def cmd_lineage():
        """Track and inspect variable lineage (origin chain)."""

    @cmd_lineage.command("record")
    @click.argument("key")
    @click.option("--source-key", required=True, help="Original key name.")
    @click.option("--source-profile", required=True, help="Profile the key originated from.")
    @click.option("--operation", required=True,
                  type=click.Choice(sorted(VALID_OPERATIONS)), help="Operation type.")
    @click.option("--note", default=None, help="Optional note.")
    @click.pass_context
    def cmd_lineage_record(ctx, key, source_key, source_profile, operation, note):
        """Record a lineage entry for KEY."""
        store_path = Path(get_store(ctx))
        entry = record_lineage(store_path, key, source_key, source_profile, operation, note)
        click.echo(f"Recorded lineage for '{key}': {entry}")

    @cmd_lineage.command("show")
    @click.argument("key")
    @click.pass_context
    def cmd_lineage_show(ctx, key):
        """Show lineage history for KEY."""
        store_path = Path(get_store(ctx))
        entries = get_lineage(store_path, key)
        if not entries:
            click.echo(f"No lineage recorded for '{key}'.")
            return
        for e in entries:
            note_str = f" | note: {e.note}" if e.note else ""
            click.echo(f"  [{e.operation}] {e.source_profile}/{e.source_key}{note_str}")

    @cmd_lineage.command("clear")
    @click.argument("key")
    @click.pass_context
    def cmd_lineage_clear(ctx, key):
        """Clear lineage history for KEY."""
        store_path = Path(get_store(ctx))
        removed = clear_lineage(store_path, key)
        if removed:
            click.echo(f"Lineage cleared for '{key}'.")
        else:
            click.echo(f"No lineage found for '{key}'.")

    @cmd_lineage.command("list")
    @click.pass_context
    def cmd_lineage_list(ctx):
        """List all keys with recorded lineage."""
        store_path = Path(get_store(ctx))
        keys = list_lineage_keys(store_path)
        if not keys:
            click.echo("No lineage records found.")
        else:
            for k in keys:
                click.echo(k)
