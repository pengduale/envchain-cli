"""CLI commands for managing variable visibility levels."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_visibility import (
    VALID_LEVELS,
    get_visibility,
    list_visibility,
    remove_visibility,
    set_visibility,
)


def register_visibility_commands(cli: click.Group, get_store) -> None:
    @cli.group("visibility")
    def cmd_visibility():
        """Manage visibility levels for environment variables."""

    @cmd_visibility.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS, case_sensitive=False))
    @click.pass_context
    def cmd_visibility_set(ctx, key: str, level: str):
        """Set the visibility level for KEY."""
        store_path = Path(get_store(ctx))
        try:
            result = set_visibility(store_path, key, level.lower())
            if result.ok:
                click.echo(f"Visibility for '{key}' set to '{result.level}'.")
            else:
                click.echo(f"Failed: {result.message}", err=True)
                ctx.exit(1)
        except ValueError as exc:
            click.echo(f"Error: {exc}", err=True)
            ctx.exit(1)

    @cmd_visibility.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_visibility_get(ctx, key: str):
        """Get the visibility level for KEY."""
        store_path = Path(get_store(ctx))
        level = get_visibility(store_path, key)
        if level is None:
            click.echo(f"No visibility set for '{key}'.")
        else:
            click.echo(level)

    @cmd_visibility.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_visibility_remove(ctx, key: str):
        """Remove the visibility setting for KEY."""
        store_path = Path(get_store(ctx))
        removed = remove_visibility(store_path, key)
        if removed:
            click.echo(f"Visibility for '{key}' removed.")
        else:
            click.echo(f"No visibility setting found for '{key}'.")

    @cmd_visibility.command("list")
    @click.pass_context
    def cmd_visibility_list(ctx):
        """List all visibility settings."""
        store_path = Path(get_store(ctx))
        mapping = list_visibility(store_path)
        if not mapping:
            click.echo("No visibility settings defined.")
        else:
            for key, level in sorted(mapping.items()):
                click.echo(f"{key}: {level}")
