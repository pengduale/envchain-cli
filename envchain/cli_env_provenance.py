"""CLI commands for managing environment variable provenance."""

from __future__ import annotations

import click

from envchain.env_provenance import (
    set_provenance,
    get_provenance,
    remove_provenance,
    list_provenance,
    VALID_ORIGINS,
)


def register_provenance_commands(cli: click.Group, get_store) -> None:
    @cli.group("provenance")
    def cmd_provenance():
        """Manage the origin/provenance of environment variables."""

    @cmd_provenance.command("set")
    @click.argument("key")
    @click.argument("origin")
    @click.option("--url", default=None, help="Source URL for the variable.")
    @click.option("--by", "recorded_by", default=None, help="Who recorded this provenance.")
    @click.option("--note", default=None, help="Optional note.")
    @click.pass_context
    def cmd_provenance_set(ctx, key, origin, url, recorded_by, note):
        """Set provenance for KEY with ORIGIN."""
        store = get_store(ctx)
        result = set_provenance(store, key, origin,
                                source_url=url,
                                recorded_by=recorded_by,
                                note=note)
        if not result.ok:
            click.echo(f"Error: {result.error}", err=True)
            ctx.exit(1)
        else:
            click.echo(f"Provenance set for '{key}': origin={origin}")

    @cmd_provenance.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_provenance_get(ctx, key):
        """Get provenance for KEY."""
        store = get_store(ctx)
        result = get_provenance(store, key)
        if result is None:
            click.echo(f"No provenance recorded for '{key}'.")
        else:
            click.echo(f"key:          {result.key}")
            click.echo(f"origin:       {result.origin}")
            click.echo(f"source_url:   {result.source_url or '-'}")
            click.echo(f"recorded_by:  {result.recorded_by or '-'}")
            click.echo(f"note:         {result.note or '-'}")

    @cmd_provenance.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_provenance_remove(ctx, key):
        """Remove provenance entry for KEY."""
        store = get_store(ctx)
        removed = remove_provenance(store, key)
        if removed:
            click.echo(f"Provenance removed for '{key}'.")
        else:
            click.echo(f"No provenance entry found for '{key}'.")

    @cmd_provenance.command("list")
    @click.pass_context
    def cmd_provenance_list(ctx):
        """List all provenance entries."""
        store = get_store(ctx)
        entries = list_provenance(store)
        if not entries:
            click.echo("No provenance entries recorded.")
        else:
            for entry in entries:
                url_part = f" ({entry.source_url})" if entry.source_url else ""
                by_part = f" by {entry.recorded_by}" if entry.recorded_by else ""
                click.echo(f"  {entry.key}: {entry.origin}{url_part}{by_part}")
