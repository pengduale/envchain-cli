"""CLI commands for namespace management."""

from __future__ import annotations

import click
from pathlib import Path
from envchain.env_namespace import (
    assign_namespace,
    get_namespace,
    remove_namespace,
    list_keys_in_namespace,
    list_namespaces,
)


def register_namespace_commands(cli: click.Group, get_store) -> None:
    cli.add_command(cmd_namespace)

    @cmd_namespace.command("set")
    @click.argument("key")
    @click.argument("namespace")
    @click.pass_context
    def cmd_namespace_set(ctx, key, namespace):
        """Assign KEY to NAMESPACE."""
        store_path = get_store(ctx)
        result = assign_namespace(store_path, key, namespace)
        if result.ok:
            click.echo(f"Assigned '{key}' to namespace '{namespace}'.")
        else:
            click.echo("Failed to assign namespace.", err=True)
            ctx.exit(1)

    @cmd_namespace.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_namespace_get(ctx, key):
        """Show the namespace for KEY."""
        store_path = get_store(ctx)
        ns = get_namespace(store_path, key)
        if ns is None:
            click.echo(f"No namespace assigned to '{key}'.")
        else:
            click.echo(ns)

    @cmd_namespace.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_namespace_remove(ctx, key):
        """Remove the namespace assignment for KEY."""
        store_path = get_store(ctx)
        removed = remove_namespace(store_path, key)
        if removed:
            click.echo(f"Removed namespace for '{key}'.")
        else:
            click.echo(f"No namespace found for '{key}'.")

    @cmd_namespace.command("list")
    @click.argument("namespace", required=False)
    @click.pass_context
    def cmd_namespace_list(ctx, namespace):
        """List all namespaces, or keys in a specific NAMESPACE."""
        store_path = get_store(ctx)
        if namespace:
            keys = list_keys_in_namespace(store_path, namespace)
            if not keys:
                click.echo(f"No keys in namespace '{namespace}'.")
            else:
                for k in keys:
                    click.echo(k)
        else:
            namespaces = list_namespaces(store_path)
            if not namespaces:
                click.echo("No namespaces defined.")
            else:
                for ns in namespaces:
                    click.echo(ns)


@click.group("namespace")
def cmd_namespace():
    """Manage variable namespaces."""
