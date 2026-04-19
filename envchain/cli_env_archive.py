"""CLI commands for archiving and restoring variables."""

from __future__ import annotations

import click

from envchain.env_archive import archive_variable, restore_variable, list_archived, purge_variable


def register_archive_commands(cli: click.Group, get_store) -> None:
    @cli.group("archive")
    def cmd_archive():
        """Archive, restore, or purge variables."""

    @cmd_archive.command("add")
    @click.argument("key")
    @click.pass_context
    def cmd_archive_add(ctx, key):
        """Archive a variable (removes it from live store)."""
        store_path, passphrase = get_store(ctx)
        from envchain.store import get_variable, delete_variable
        val = get_variable(store_path, key, passphrase)
        if val is None:
            raise click.ClickException(f"Key '{key}' not found in store.")
        from envchain.store import _load_raw
        raw = _load_raw(store_path)
        encrypted = raw.get(key)
        if encrypted is None:
            raise click.ClickException(f"Key '{key}' not found in raw store.")
        archive_variable(store_path, key, encrypted)
        delete_variable(store_path, key)
        click.echo(f"Archived '{key}'.")

    @cmd_archive.command("restore")
    @click.argument("key")
    @click.pass_context
    def cmd_archive_restore(ctx, key):
        """Restore a variable from archive back to live store."""
        store_path, _ = get_store(ctx)
        result = restore_variable(store_path, key)
        if not result.ok:
            raise click.ClickException(f"Cannot restore '{key}': {result.reason}")
        from envchain.store import _load_raw, _save_raw
        raw = _load_raw(store_path)
        raw[key] = result.reason
        _save_raw(store_path, raw)
        click.echo(f"Restored '{key}' to live store.")

    @cmd_archive.command("list")
    @click.pass_context
    def cmd_archive_list(ctx):
        """List archived variable keys."""
        store_path, _ = get_store(ctx)
        keys = list_archived(store_path)
        if not keys:
            click.echo("No archived variables.")
        for k in keys:
            click.echo(k)

    @cmd_archive.command("purge")
    @click.argument("key")
    @click.pass_context
    def cmd_archive_purge(ctx, key):
        """Permanently delete a variable from the archive."""
        store_path, _ = get_store(ctx)
        result = purge_variable(store_path, key)
        if not result.ok:
            raise click.ClickException(f"Cannot purge '{key}': {result.reason}")
        click.echo(f"Purged '{key}' from archive.")
