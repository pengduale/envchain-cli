"""CLI commands for maturity level management."""
import click

from .env_maturity import (
    VALID_LEVELS,
    filter_by_level,
    get_maturity,
    list_maturity,
    remove_maturity,
    set_maturity,
)


def register_maturity_commands(cli, get_store):
    @cli.group("maturity")
    def cmd_maturity():
        """Manage maturity levels for environment variable keys."""

    @cmd_maturity.command("set")
    @click.argument("key")
    @click.argument("level", type=click.Choice(VALID_LEVELS))
    @click.option("--note", default=None, help="Optional note about the maturity level.")
    @click.pass_context
    def cmd_maturity_set(ctx, key, level, note):
        """Set the maturity level for KEY."""
        store_path = get_store(ctx)
        try:
            result = set_maturity(store_path, key, level, note)
            click.echo(f"Set maturity for '{result.key}': {result.level}")
            if result.note:
                click.echo(f"  Note: {result.note}")
        except ValueError as exc:
            raise click.ClickException(str(exc))

    @cmd_maturity.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_maturity_get(ctx, key):
        """Get the maturity level for KEY."""
        store_path = get_store(ctx)
        result = get_maturity(store_path, key)
        if result is None:
            raise click.ClickException(f"No maturity level set for '{key}'.")
        click.echo(f"{result.key}: {result.level}")
        if result.note:
            click.echo(f"  Note: {result.note}")

    @cmd_maturity.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_maturity_remove(ctx, key):
        """Remove the maturity level for KEY."""
        store_path = get_store(ctx)
        removed = remove_maturity(store_path, key)
        if removed:
            click.echo(f"Removed maturity level for '{key}'.")
        else:
            raise click.ClickException(f"No maturity level found for '{key}'.")

    @cmd_maturity.command("list")
    @click.option("--filter", "level_filter", type=click.Choice(VALID_LEVELS), default=None)
    @click.pass_context
    def cmd_maturity_list(ctx, level_filter):
        """List all keys with maturity levels, optionally filtered."""
        store_path = get_store(ctx)
        results = filter_by_level(store_path, level_filter) if level_filter else list_maturity(store_path)
        if not results:
            click.echo("No maturity levels recorded.")
            return
        for r in results:
            note_part = f"  # {r.note}" if r.note else ""
            click.echo(f"  {r.key}: {r.level}{note_part}")
