"""CLI commands for staleness tracking."""

from __future__ import annotations

import click
from pathlib import Path

from envchain.env_staleness import (
    touch_key,
    set_threshold,
    check_staleness,
    list_stale,
)


def register_staleness_commands(cli, get_store):
    @cli.group("staleness")
    def cmd_staleness():
        """Track and report variable staleness."""

    @cmd_staleness.command("touch")
    @click.argument("key")
    @click.pass_context
    def cmd_touch(ctx, key):
        """Mark KEY as freshly updated (resets its age)."""
        store_path = get_store(ctx)
        result = touch_key(Path(store_path), key)
        click.echo(f"Touched '{key}' — age reset to 0 days.")

    @cmd_staleness.command("set-threshold")
    @click.argument("key")
    @click.argument("days", type=int)
    @click.pass_context
    def cmd_set_threshold(ctx, key, days):
        """Set staleness threshold for KEY to DAYS days."""
        store_path = get_store(ctx)
        try:
            result = set_threshold(Path(store_path), key, days)
            click.echo(f"Threshold for '{key}' set to {days} day(s).")
        except ValueError as exc:
            raise click.ClickException(str(exc))

    @cmd_staleness.command("check")
    @click.argument("key")
    @click.pass_context
    def cmd_check(ctx, key):
        """Check staleness status of KEY."""
        store_path = get_store(ctx)
        result = check_staleness(Path(store_path), key)
        if result is None:
            click.echo(f"No staleness record for '{key}'.")
            return
        status = "STALE" if result.is_stale else "fresh"
        click.echo(
            f"Key: {key}\n"
            f"Age: {result.age_days:.1f} day(s)\n"
            f"Threshold: {result.threshold_days} day(s)\n"
            f"Status: {status}"
        )

    @cmd_staleness.command("list-stale")
    @click.pass_context
    def cmd_list_stale(ctx):
        """List all keys that have exceeded their staleness threshold."""
        store_path = get_store(ctx)
        stale = list_stale(Path(store_path))
        if not stale:
            click.echo("No stale keys found.")
            return
        for r in stale:
            click.echo(f"{r.key}: {r.age_days:.1f} day(s) old (threshold: {r.threshold_days})")
