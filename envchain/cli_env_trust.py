"""CLI commands for trust-level management."""

from __future__ import annotations

from pathlib import Path

import click

from .env_trust import VALID_LEVELS, get_trust, list_trust, remove_trust, set_trust


def register_trust_commands(cli: click.Group, get_store):
    @cli.group("trust")
    def cmd_trust():
        """Manage trust levels for environment variable keys."""

    @cmd_trust.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS))
    @click.pass_context
    def cmd_trust_set(ctx, key: str, level: str):
        """Set the trust level for KEY."""
        store_path = Path(get_store(ctx))
        try:
            result = set_trust(store_path, key, level)
            click.echo(f"[ok] {result.message}" if result.ok else f"[error] {result.message}")
        except ValueError as exc:
            raise click.ClickException(str(exc))

    @cmd_trust.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_trust_get(ctx, key: str):
        """Get the trust level for KEY."""
        store_path = Path(get_store(ctx))
        level = get_trust(store_path, key)
        if level is None:
            click.echo(f"No trust level set for '{key}'")
        else:
            click.echo(level)

    @cmd_trust.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_trust_remove(ctx, key: str):
        """Remove the trust level for KEY."""
        store_path = Path(get_store(ctx))
        removed = remove_trust(store_path, key)
        if removed:
            click.echo(f"[ok] Trust level removed for '{key}'")
        else:
            click.echo(f"No trust level found for '{key}'")

    @cmd_trust.command("list")
    @click.pass_context
    def cmd_trust_list(ctx):
        """List all keys with assigned trust levels."""
        store_path = Path(get_store(ctx))
        mapping = list_trust(store_path)
        if not mapping:
            click.echo("No trust levels assigned.")
            return
        for key, level in sorted(mapping.items()):
            click.echo(f"{key}: {level}")
