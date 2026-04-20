"""CLI commands for variable change history."""
from __future__ import annotations

import time
import click
from pathlib import Path

from envchain.env_history import (
    get_history,
    clear_history,
    list_keys_with_history,
)


def register_history_commands(cli: click.Group, get_store) -> None:
    """Attach history sub-commands to *cli*."""

    @cli.group("history")
    def cmd_history():
        """View or clear variable change history."""

    @cmd_history.command("show")
    @click.argument("key")
    @click.option("--store", "store_path", default=None, help="Path to store file.")
    @click.pass_context
    def cmd_history_show(ctx, key: str, store_path: str | None):
        """Show change history for KEY."""
        sp = Path(store_path) if store_path else get_store(ctx)
        entries = get_history(sp, key)
        if not entries:
            click.echo(f"No history found for '{key}'.")
            return
        click.echo(f"History for '{key}' ({len(entries)} entries):")
        for e in entries:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e.timestamp))
            preview = f"  preview={e.preview}" if e.preview else ""
            click.echo(f"  [{ts}] {e.action.upper()}{preview}")

    @cmd_history.command("list")
    @click.option("--store", "store_path", default=None, help="Path to store file.")
    @click.pass_context
    def cmd_history_list(ctx, store_path: str | None):
        """List all keys that have recorded history."""
        sp = Path(store_path) if store_path else get_store(ctx)
        keys = list_keys_with_history(sp)
        if not keys:
            click.echo("No history recorded yet.")
            return
        for k in sorted(keys):
            click.echo(k)

    @cmd_history.command("clear")
    @click.argument("key", required=False, default=None)
    @click.option("--all", "clear_all", is_flag=True, help="Clear history for all keys.")
    @click.option("--store", "store_path", default=None, help="Path to store file.")
    @click.pass_context
    def cmd_history_clear(ctx, key: str | None, clear_all: bool, store_path: str | None):
        """Clear history for KEY or all keys (--all)."""
        if not key and not clear_all:
            raise click.UsageError("Provide a KEY or pass --all.")
        sp = Path(store_path) if store_path else get_store(ctx)
        removed = clear_history(sp, key=None if clear_all else key)
        scope = "all keys" if clear_all else f"'{key}'"
        click.echo(f"Cleared {removed} history entries for {scope}.")
