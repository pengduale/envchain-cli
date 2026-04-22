"""CLI commands for managing variable sensitivity levels."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_sensitivity import (
    VALID_LEVELS,
    get_keys_by_level,
    get_sensitivity,
    list_sensitivity,
    remove_sensitivity,
    set_sensitivity,
)


def register_sensitivity_commands(cli, get_store):
    @cli.group("sensitivity")
    def cmd_sensitivity():
        """Manage sensitivity levels for environment variables."""

    @cmd_sensitivity.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS))
    @click.pass_context
    def cmd_sensitivity_set(ctx, key, level):
        """Set sensitivity level for a variable."""
        store_path = Path(get_store(ctx))
        result = set_sensitivity(store_path, key, level)
        if result.ok:
            click.echo(f"Sensitivity for '{key}' set to '{level}'.")
        else:
            click.echo(f"Error: {result.message}", err=True)

    @cmd_sensitivity.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_sensitivity_get(ctx, key):
        """Get sensitivity level for a variable."""
        store_path = Path(get_store(ctx))
        level = get_sensitivity(store_path, key)
        if level is None:
            click.echo(f"No sensitivity level set for '{key}'.")
        else:
            click.echo(level)

    @cmd_sensitivity.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_sensitivity_remove(ctx, key):
        """Remove sensitivity level for a variable."""
        store_path = Path(get_store(ctx))
        removed = remove_sensitivity(store_path, key)
        if removed:
            click.echo(f"Sensitivity for '{key}' removed.")
        else:
            click.echo(f"No sensitivity entry found for '{key}'.")

    @cmd_sensitivity.command("list")
    @click.option("--level", type=click.Choice(VALID_LEVELS), default=None, help="Filter by level.")
    @click.pass_context
    def cmd_sensitivity_list(ctx, level):
        """List all sensitivity levels, optionally filtered."""
        store_path = Path(get_store(ctx))
        if level:
            keys = get_keys_by_level(store_path, level)
            if not keys:
                click.echo(f"No variables with sensitivity '{level}'.")
            else:
                for k in keys:
                    click.echo(f"{k}: {level}")
        else:
            data = list_sensitivity(store_path)
            if not data:
                click.echo("No sensitivity levels defined.")
            else:
                for k, v in sorted(data.items()):
                    click.echo(f"{k}: {v}")
