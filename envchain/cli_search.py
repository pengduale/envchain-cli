"""CLI commands for searching environment variables."""

from __future__ import annotations

import click

from envchain.cli import _get_store
from envchain.search import search_default, search_profile, search_all_profiles


def register_search_commands(cli: click.Group) -> None:
    cli.add_command(cmd_search)


@click.command("search")
@click.argument("pattern")
@click.option("--profile", "-p", default=None, help="Limit search to a specific profile.")
@click.option("--all-profiles", "-A", "all_profiles", is_flag=True, help="Search across all profiles.")
@click.option("--show-values", "-v", is_flag=True, help="Print decrypted values alongside keys.")
@click.pass_context
def cmd_search(ctx: click.Context, pattern: str, profile: str | None, all_profiles: bool, show_values: bool) -> None:
    """Search for keys matching PATTERN (supports shell wildcards like '*', '?')."""
    store_path, passphrase = _get_store(ctx)

    def _print_hits(source: str, hits: list) -> None:
        if not hits:
            return
        click.echo(f"[{source}]")
        for key, value in hits:
            if show_values:
                click.echo(f"  {key}={value}")
            else:
                click.echo(f"  {key}")

    if all_profiles:
        results = search_all_profiles(pattern, passphrase, store_path)
        if not results:
            click.echo("No matches found.")
            return
        for source, hits in results.items():
            _print_hits(source, hits)
    elif profile:
        hits = search_profile(pattern, passphrase, store_path, profile)
        if not hits:
            click.echo("No matches found.")
            return
        _print_hits(profile, hits)
    else:
        hits = search_default(pattern, passphrase, store_path)
        if not hits:
            click.echo("No matches found.")
            return
        _print_hits("default", hits)
