"""CLI commands for managing environment variable dependencies."""
from __future__ import annotations

from pathlib import Path

import click

from envchain.env_dependency import (
    add_dependency,
    check_dependencies,
    get_dependencies,
    list_all_dependencies,
    remove_dependency,
)
from envchain.store import list_keys


def register_dependency_commands(cli: click.Group, get_store) -> None:
    @cli.group("dep")
    def cmd_dep():
        """Manage variable dependencies."""

    @cmd_dep.command("add")
    @click.argument("key")
    @click.argument("depends_on")
    @click.pass_context
    def cmd_dep_add(ctx, key: str, depends_on: str):
        """Declare that KEY depends on DEPENDS_ON."""
        store_path = get_store(ctx)
        result = add_dependency(store_path, key, depends_on)
        click.echo(f"Added: {key} -> {depends_on}")

    @cmd_dep.command("remove")
    @click.argument("key")
    @click.argument("depends_on")
    @click.pass_context
    def cmd_dep_remove(ctx, key: str, depends_on: str):
        """Remove the dependency of KEY on DEPENDS_ON."""
        store_path = get_store(ctx)
        removed = remove_dependency(store_path, key, depends_on)
        if removed:
            click.echo(f"Removed: {key} -> {depends_on}")
        else:
            click.echo(f"Dependency not found: {key} -> {depends_on}")

    @cmd_dep.command("show")
    @click.argument("key")
    @click.pass_context
    def cmd_dep_show(ctx, key: str):
        """Show dependencies for KEY."""
        store_path = get_store(ctx)
        deps = get_dependencies(store_path, key)
        if not deps:
            click.echo(f"{key} has no dependencies.")
        else:
            click.echo(f"{key} depends on:")
            for d in deps:
                click.echo(f"  - {d}")

    @cmd_dep.command("list")
    @click.pass_context
    def cmd_dep_list(ctx):
        """List all declared dependencies."""
        store_path = get_store(ctx)
        all_deps = list_all_dependencies(store_path)
        if not all_deps:
            click.echo("No dependencies defined.")
            return
        for key, deps in sorted(all_deps.items()):
            click.echo(f"{key}: {', '.join(deps)}")

    @cmd_dep.command("check")
    @click.argument("key")
    @click.pass_context
    def cmd_dep_check(ctx, key: str):
        """Check whether all dependencies of KEY are present in the store."""
        store_path = get_store(ctx)
        present = list_keys(store_path)
        result = check_dependencies(store_path, key, present)
        if result.ok:
            click.echo(f"OK: {result.message}")
        else:
            click.echo(f"FAIL: {result.message}", err=True)
            raise SystemExit(1)
