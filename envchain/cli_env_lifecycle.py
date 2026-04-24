"""CLI commands for lifecycle state management."""

from __future__ import annotations

import click
from pathlib import Path

from envchain.env_lifecycle import (
    set_lifecycle,
    get_lifecycle,
    remove_lifecycle,
    list_by_state,
    list_all_lifecycle,
    VALID_STATES,
)


def register_lifecycle_commands(cli, get_store):
    @cli.group("lifecycle")
    def cmd_lifecycle():
        """Manage variable lifecycle states (active, deprecated, retired, draft)."""

    @cmd_lifecycle.command("set")
    @click.argument("key")
    @click.argument("state", type=click.Choice(VALID_STATES))
    @click.pass_context
    def cmd_lifecycle_set(ctx, key, state):
        """Set lifecycle state for KEY."""
        store_path = get_store(ctx)
        try:
            result = set_lifecycle(Path(store_path), key, state)
            click.echo(f"[ok] {result.message}")
        except ValueError as e:
            raise click.ClickException(str(e))

    @cmd_lifecycle.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_lifecycle_get(ctx, key):
        """Get lifecycle state for KEY."""
        store_path = get_store(ctx)
        state = get_lifecycle(Path(store_path), key)
        if state is None:
            click.echo(f"[unset] {key} has no lifecycle state.")
        else:
            click.echo(f"{key}: {state}")

    @cmd_lifecycle.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_lifecycle_remove(ctx, key):
        """Remove lifecycle state for KEY."""
        store_path = get_store(ctx)
        removed = remove_lifecycle(Path(store_path), key)
        if removed:
            click.echo(f"[ok] Lifecycle state removed for {key!r}.")
        else:
            click.echo(f"[warn] No lifecycle state found for {key!r}.")

    @cmd_lifecycle.command("list")
    @click.option("--state", type=click.Choice(VALID_STATES), default=None, help="Filter by state.")
    @click.pass_context
    def cmd_lifecycle_list(ctx, state):
        """List all keys with lifecycle states, optionally filtered."""
        store_path = get_store(ctx)
        if state:
            keys = list_by_state(Path(store_path), state)
            if not keys:
                click.echo(f"No keys with state {state!r}.")
            for k in keys:
                click.echo(f"{k}: {state}")
        else:
            data = list_all_lifecycle(Path(store_path))
            if not data:
                click.echo("No lifecycle states defined.")
            for k, v in sorted(data.items()):
                click.echo(f"{k}: {v}")
