"""CLI commands for env risk scoring."""
from __future__ import annotations

from pathlib import Path

import click

from envchain.env_risk import VALID_LEVELS, get_risk, list_risk, remove_risk, set_risk


def register_risk_commands(cli: click.Group, get_store) -> None:
    @cli.group("risk")
    def cmd_risk():
        """Manage risk levels for environment variables."""

    @cmd_risk.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS))
    @click.option("--reason", default="", help="Optional reason for this risk level.")
    @click.pass_context
    def cmd_risk_set(ctx, key, level, reason):
        """Assign a risk level to KEY."""
        store_path = Path(get_store(ctx))
        result = set_risk(store_path, key, level, reason)
        if not result.ok:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)
        else:
            click.echo(f"Risk for '{key}' set to '{level}'.")

    @cmd_risk.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_risk_get(ctx, key):
        """Get the risk level for KEY."""
        store_path = Path(get_store(ctx))
        result = get_risk(store_path, key)
        if result is None:
            click.echo(f"No risk entry for '{key}'.")
        else:
            reason_str = f" ({result.reason})" if result.reason else ""
            click.echo(f"{key}: {result.level}{reason_str}")

    @cmd_risk.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_risk_remove(ctx, key):
        """Remove the risk entry for KEY."""
        store_path = Path(get_store(ctx))
        removed = remove_risk(store_path, key)
        if removed:
            click.echo(f"Risk entry for '{key}' removed.")
        else:
            click.echo(f"No risk entry found for '{key}'.")

    @cmd_risk.command("list")
    @click.pass_context
    def cmd_risk_list(ctx):
        """List all risk entries."""
        store_path = Path(get_store(ctx))
        entries = list_risk(store_path)
        if not entries:
            click.echo("No risk entries recorded.")
            return
        for e in entries:
            reason_str = f" — {e.reason}" if e.reason else ""
            click.echo(f"{e.key}: {e.level}{reason_str}")
