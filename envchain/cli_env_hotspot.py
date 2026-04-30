"""CLI commands for env-hotspot (frequently accessed keys)."""

from __future__ import annotations

import click

from envchain.env_hotspot import get_count, record_access, reset_hotspots, top_keys


def register_hotspot_commands(cli: click.Group, get_store) -> None:  # noqa: ANN001
    @cli.group("hotspot")
    def cmd_hotspot() -> None:
        """Track and inspect frequently accessed keys."""

    @cmd_hotspot.command("record")
    @click.argument("key")
    @click.pass_context
    def cmd_record(ctx: click.Context, key: str) -> None:
        """Record an access event for KEY."""
        store = get_store(ctx)
        result = record_access(store, key)
        if not result.ok:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)
        click.echo(f"Recorded access for '{key}' (total: {result.count})")

    @cmd_hotspot.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_get(ctx: click.Context, key: str) -> None:
        """Show the access count for KEY."""
        store = get_store(ctx)
        count = get_count(store, key)
        if count is None:
            click.echo(f"'{key}' has never been accessed.")
        else:
            click.echo(f"{key}: {count}")

    @cmd_hotspot.command("top")
    @click.option("--limit", "-n", default=10, show_default=True, help="Number of keys to show.")
    @click.pass_context
    def cmd_top(ctx: click.Context, limit: int) -> None:
        """List the top N most-accessed keys."""
        store = get_store(ctx)
        results = top_keys(store, n=limit)
        if not results:
            click.echo("No hotspot data recorded yet.")
            return
        click.echo(f"{'Rank':<6} {'Key':<40} {'Accesses':>8}")
        click.echo("-" * 56)
        for rank, r in enumerate(results, start=1):
            click.echo(f"{rank:<6} {r.key:<40} {r.count:>8}")

    @cmd_hotspot.command("reset")
    @click.confirmation_option(prompt="Clear all hotspot data?")
    @click.pass_context
    def cmd_reset(ctx: click.Context) -> None:
        """Clear all hotspot counters."""
        store = get_store(ctx)
        removed = reset_hotspots(store)
        click.echo(f"Cleared {removed} hotspot record(s).")
