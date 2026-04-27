"""CLI commands for the badge annotation feature."""

from __future__ import annotations

import click
from pathlib import Path

from envchain.env_badge import (
    VALID_BADGES,
    add_badge,
    remove_badge,
    get_badges,
    list_all_badges,
)


def register_badge_commands(cli: click.Group, get_store) -> None:
    @cli.group("badge")
    def cmd_badge():
        """Manage status badges on environment variables."""

    @cmd_badge.command("add")
    @click.argument("key")
    @click.argument("badge")
    @click.pass_context
    def cmd_badge_add(ctx, key: str, badge: str):
        """Add a badge to KEY."""
        store_path = get_store(ctx)
        try:
            result = add_badge(Path(store_path), key, badge)
        except ValueError as exc:
            raise click.ClickException(str(exc))
        if result.ok:
            click.echo(f"[ok] {result.message}")
        else:
            click.echo(f"[warn] {result.message}")

    @cmd_badge.command("remove")
    @click.argument("key")
    @click.argument("badge")
    @click.pass_context
    def cmd_badge_remove(ctx, key: str, badge: str):
        """Remove a badge from KEY."""
        store_path = get_store(ctx)
        result = remove_badge(Path(store_path), key, badge)
        if result.ok:
            click.echo(f"[ok] {result.message}")
        else:
            click.echo(f"[warn] {result.message}")

    @cmd_badge.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_badge_get(ctx, key: str):
        """List badges for KEY."""
        store_path = get_store(ctx)
        badges = get_badges(Path(store_path), key)
        if not badges:
            click.echo(f"No badges for '{key}'.")
        else:
            click.echo(", ".join(sorted(badges)))

    @cmd_badge.command("list")
    @click.pass_context
    def cmd_badge_list(ctx):
        """List all keys with badges."""
        store_path = get_store(ctx)
        all_badges = list_all_badges(Path(store_path))
        if not all_badges:
            click.echo("No badges defined.")
            return
        for key, badges in sorted(all_badges.items()):
            click.echo(f"{key}: {', '.join(sorted(badges))}")

    @cmd_badge.command("valid")
    def cmd_badge_valid():
        """Show all valid badge names."""
        for b in sorted(VALID_BADGES):
            click.echo(b)
