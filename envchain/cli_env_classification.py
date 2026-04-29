"""CLI commands for managing variable classification levels."""

from __future__ import annotations

import click

from envchain.env_classification import (
    VALID_LEVELS,
    get_classification,
    list_classifications,
    remove_classification,
    set_classification,
)


def register_classification_commands(cli: click.Group, get_store) -> None:
    @cli.group("classification")
    def cmd_classification():
        """Manage variable classification levels."""

    @cmd_classification.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS))
    @click.pass_context
    def cmd_classification_set(ctx, key: str, level: str):
        """Set the classification level for KEY."""
        store_path = get_store(ctx)
        result = set_classification(store_path, key, level)
        if result.ok:
            click.echo(f"Classification for '{key}' set to '{level}'.")
        else:
            click.echo(f"Error: {result.message}", err=True)
            ctx.exit(1)

    @cmd_classification.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_classification_get(ctx, key: str):
        """Get the classification level for KEY."""
        store_path = get_store(ctx)
        level = get_classification(store_path, key)
        if level is None:
            click.echo(f"No classification set for '{key}'.")
        else:
            click.echo(level)

    @cmd_classification.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_classification_remove(ctx, key: str):
        """Remove the classification for KEY."""
        store_path = get_store(ctx)
        removed = remove_classification(store_path, key)
        if removed:
            click.echo(f"Classification for '{key}' removed.")
        else:
            click.echo(f"No classification found for '{key}'.")

    @cmd_classification.command("list")
    @click.pass_context
    def cmd_classification_list(ctx):
        """List all classified variables."""
        store_path = get_store(ctx)
        data = list_classifications(store_path)
        if not data:
            click.echo("No classifications set.")
            return
        for k, v in sorted(data.items()):
            click.echo(f"{k}: {v}")
