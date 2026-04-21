"""CLI commands for checkpoint management."""

from __future__ import annotations

import click
from pathlib import Path

from envchain.env_checkpoint import (
    create_checkpoint,
    restore_checkpoint,
    list_checkpoints,
    delete_checkpoint,
)


def register_checkpoint_commands(cli: click.Group, get_store) -> None:
    cli.add_command(cmd_checkpoint)

    @cmd_checkpoint.command("create")
    @click.argument("name")
    @click.option("--profile", default="default", show_default=True)
    @click.pass_context
    def _create(ctx, name, profile):
        """Save current variables to a named checkpoint."""
        store_path, passphrase = get_store(ctx)
        result = create_checkpoint(Path(store_path), passphrase, name, profile=profile)
        if result.ok:
            click.echo(f"Checkpoint '{name}' created with {result.keys_saved} key(s).")
        else:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)

    @cmd_checkpoint.command("restore")
    @click.argument("name")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.pass_context
    def _restore(ctx, name, overwrite):
        """Restore variables from a named checkpoint."""
        store_path, passphrase = get_store(ctx)
        result = restore_checkpoint(Path(store_path), passphrase, name, overwrite=overwrite)
        if result.ok:
            click.echo(f"Restored {result.keys_saved} key(s) from checkpoint '{name}'.")
        else:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)

    @cmd_checkpoint.command("list")
    @click.pass_context
    def _list(ctx):
        """List all available checkpoints."""
        store_path, _ = get_store(ctx)
        items = list_checkpoints(Path(store_path))
        if not items:
            click.echo("No checkpoints found.")
            return
        for item in items:
            click.echo(f"{item['name']}  profile={item['profile']}  keys={item['keys']}")

    @cmd_checkpoint.command("delete")
    @click.argument("name")
    @click.pass_context
    def _delete(ctx, name):
        """Delete a named checkpoint."""
        store_path, _ = get_store(ctx)
        if delete_checkpoint(Path(store_path), name):
            click.echo(f"Checkpoint '{name}' deleted.")
        else:
            click.echo(f"Checkpoint '{name}' not found.", err=True)
            ctx.exit(1)


@click.group("checkpoint")
def cmd_checkpoint():
    """Manage variable checkpoints."""
