"""CLI commands for env-changelog feature."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_changelog import (
    add_changelog_entry,
    get_changelog_entries,
    clear_changelog,
    list_keys_with_changelog,
)


def register_changelog_commands(cli: click.Group, get_store) -> None:
    @cli.group("changelog")
    def cmd_changelog():
        """Manage human-readable changelog entries for variables."""

    @cmd_changelog.command("add")
    @click.argument("key")
    @click.argument("message")
    @click.option("--author", default=None, help="Author of the change.")
    @click.pass_context
    def cmd_changelog_add(ctx, key, message, author):
        """Add a changelog entry for KEY."""
        store_path = get_store(ctx)
        entry = add_changelog_entry(store_path, key, message, author=author)
        click.echo(f"Added: {entry}")

    @cmd_changelog.command("show")
    @click.argument("key")
    @click.pass_context
    def cmd_changelog_show(ctx, key):
        """Show all changelog entries for KEY."""
        store_path = get_store(ctx)
        entries = get_changelog_entries(store_path, key)
        if not entries:
            click.echo(f"No changelog entries for '{key}'.")
            return
        for e in entries:
            click.echo(str(e))

    @cmd_changelog.command("clear")
    @click.argument("key")
    @click.pass_context
    def cmd_changelog_clear(ctx, key):
        """Clear all changelog entries for KEY."""
        store_path = get_store(ctx)
        removed = clear_changelog(store_path, key)
        if removed:
            click.echo(f"Changelog cleared for '{key}'.")
        else:
            click.echo(f"No changelog found for '{key}'.")

    @cmd_changelog.command("list")
    @click.pass_context
    def cmd_changelog_list(ctx):
        """List all keys that have changelog entries."""
        store_path = get_store(ctx)
        keys = list_keys_with_changelog(store_path)
        if not keys:
            click.echo("No changelog entries found.")
            return
        for k in keys:
            click.echo(k)
