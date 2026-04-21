"""CLI commands for the env-rating feature."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_rating import (
    average_rating,
    get_rating,
    list_ratings,
    remove_rating,
    set_rating,
)


def register_rating_commands(cli: click.Group, get_store) -> None:
    """Attach the ``rating`` command group to *cli*."""

    @cli.group("rating")
    def cmd_rating() -> None:
        """Manage per-key quality ratings (1-5 stars)."""

    @cmd_rating.command("set")
    @click.argument("key")
    @click.argument("stars", type=click.IntRange(1, 5))
    @click.pass_context
    def cmd_rating_set(ctx: click.Context, key: str, stars: int) -> None:
        """Set a 1-5 star rating for KEY."""
        store_path: Path = get_store(ctx)
        result = set_rating(store_path, key, stars)
        click.echo(f"Rated '{key}': {'★' * stars}{'☆' * (5 - stars)}")

    @cmd_rating.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_rating_get(ctx: click.Context, key: str) -> None:
        """Show the rating for KEY."""
        store_path: Path = get_store(ctx)
        rating = get_rating(store_path, key)
        if rating is None:
            click.echo(f"No rating for '{key}'.")
        else:
            click.echo(f"{'★' * rating}{'☆' * (5 - rating)} ({rating}/5)")

    @cmd_rating.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_rating_remove(ctx: click.Context, key: str) -> None:
        """Remove the rating for KEY."""
        store_path: Path = get_store(ctx)
        removed = remove_rating(store_path, key)
        if removed:
            click.echo(f"Rating for '{key}' removed.")
        else:
            click.echo(f"No rating found for '{key}'.")

    @cmd_rating.command("list")
    @click.pass_context
    def cmd_rating_list(ctx: click.Context) -> None:
        """List all rated keys."""
        store_path: Path = get_store(ctx)
        ratings = list_ratings(store_path)
        if not ratings:
            click.echo("No ratings recorded.")
            return
        for key, stars in sorted(ratings.items()):
            click.echo(f"  {key}: {'★' * stars}{'☆' * (5 - stars)}")
        avg = average_rating(store_path)
        click.echo(f"\nAverage: {avg:.2f}/5")
