"""CLI commands for env cost tracking."""

from __future__ import annotations

import click
from pathlib import Path

from envchain.env_cost import set_cost, get_cost, remove_cost, list_costs


def register_cost_commands(cli: click.Group, get_store) -> None:
    @cli.group("cost")
    def cmd_cost():
        """Manage cost/billing metadata for variables."""

    @cmd_cost.command("set")
    @click.argument("key")
    @click.argument("amount", type=float)
    @click.option("--currency", default="USD", show_default=True, help="Currency code (e.g. USD, EUR).")
    @click.option("--note", default=None, help="Optional note about the cost.")
    @click.pass_context
    def cmd_cost_set(ctx, key, amount, currency, note):
        """Set cost metadata for a variable KEY."""
        store_path = get_store(ctx)
        result = set_cost(store_path, key, amount, currency, note)
        if not result.ok:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)
        else:
            note_str = f" ({note})" if note else ""
            click.echo(f"Set cost for '{key}': {amount} {currency}{note_str}")

    @cmd_cost.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_cost_get(ctx, key):
        """Get cost metadata for a variable KEY."""
        store_path = get_store(ctx)
        result = get_cost(store_path, key)
        if result is None:
            click.echo(f"No cost metadata found for '{key}'.")
        else:
            note_str = f"  # {result.note}" if result.note else ""
            click.echo(f"{key}: {result.amount} {result.currency}{note_str}")

    @cmd_cost.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_cost_remove(ctx, key):
        """Remove cost metadata for a variable KEY."""
        store_path = get_store(ctx)
        removed = remove_cost(store_path, key)
        if removed:
            click.echo(f"Removed cost metadata for '{key}'.")
        else:
            click.echo(f"No cost metadata found for '{key}'.")

    @cmd_cost.command("list")
    @click.pass_context
    def cmd_cost_list(ctx):
        """List all variables with cost metadata."""
        store_path = get_store(ctx)
        results = list_costs(store_path)
        if not results:
            click.echo("No cost metadata recorded.")
        else:
            for r in results:
                note_str = f"  # {r.note}" if r.note else ""
                click.echo(f"{r.key}: {r.amount} {r.currency}{note_str}")
