"""CLI commands for managing read-only variable locks."""

from __future__ import annotations

import click
from pathlib import Path

from envchain.env_readonly import (
    set_readonly,
    is_readonly,
    remove_readonly,
    list_readonly_keys,
)


def register_readonly_commands(cli: click.Group, get_store) -> None:
    cli.add_command(cmd_readonly)

    @cmd_readonly.command("set")
    @click.argument("key")
    @click.pass_context
    def cmd_readonly_set(ctx, key):
        """Mark KEY as read-only."""
        store_path = get_store(ctx)
        result = set_readonly(store_path, key, locked=True)
        if result.ok:
            click.echo(f"[locked] {result.message}")
        else:
            click.echo(f"[error] {result.message}", err=True)

    @cmd_readonly.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_readonly_remove(ctx, key):
        """Remove the read-only lock from KEY."""
        store_path = get_store(ctx)
        result = remove_readonly(store_path, key)
        if result.ok:
            click.echo(f"[unlocked] {result.message}")
        else:
            click.echo(f"[error] {result.message}", err=True)

    @cmd_readonly.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_readonly_get(ctx, key):
        """Check whether KEY is read-only."""
        store_path = get_store(ctx)
        locked = is_readonly(store_path, key)
        status = "read-only" if locked else "writable"
        click.echo(f"{key}: {status}")

    @cmd_readonly.command("list")
    @click.pass_context
    def cmd_readonly_list(ctx):
        """List all keys marked as read-only."""
        store_path = get_store(ctx)
        keys = list_readonly_keys(store_path)
        if not keys:
            click.echo("No read-only keys.")
        else:
            for k in keys:
                click.echo(f"  {k}")


@click.group("readonly")
def cmd_readonly():
    """Manage read-only locks on variables."""
