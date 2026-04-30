"""CLI commands for env criticality management."""

from __future__ import annotations

import click

from envchain.env_criticality import (
    VALID_LEVELS,
    get_criticality,
    list_criticality,
    remove_criticality,
    set_criticality,
)


def register_criticality_commands(cli: click.Group, get_store) -> None:
    @cli.group("criticality")
    def cmd_criticality():
        """Manage criticality levels for environment variables."""

    @cmd_criticality.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS))
    @click.option("--reason", default=None, help="Optional reason for this criticality level.")
    @click.pass_context
    def cmd_criticality_set(ctx, key, level, reason):
        """Set criticality level for KEY."""
        store_path = get_store(ctx)
        result = set_criticality(store_path, key, level, reason)
        if not result.ok:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)
        else:
            msg = f"Set criticality for '{key}': {level}"
            if reason:
                msg += f" ({reason})"
            click.echo(msg)

    @cmd_criticality.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_criticality_get(ctx, key):
        """Get criticality level for KEY."""
        store_path = get_store(ctx)
        result = get_criticality(store_path, key)
        if result is None:
            click.echo(f"No criticality set for '{key}'.")
        else:
            line = f"{key}: {result.level}"
            if result.reason:
                line += f" — {result.reason}"
            click.echo(line)

    @cmd_criticality.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_criticality_remove(ctx, key):
        """Remove criticality level for KEY."""
        store_path = get_store(ctx)
        removed = remove_criticality(store_path, key)
        if removed:
            click.echo(f"Removed criticality for '{key}'.")
        else:
            click.echo(f"No criticality entry found for '{key}'.")

    @cmd_criticality.command("list")
    @click.pass_context
    def cmd_criticality_list(ctx):
        """List all criticality levels."""
        store_path = get_store(ctx)
        entries = list_criticality(store_path)
        if not entries:
            click.echo("No criticality levels set.")
            return
        for entry in entries:
            line = f"{entry.key}: {entry.level}"
            if entry.reason:
                line += f" — {entry.reason}"
            click.echo(line)
