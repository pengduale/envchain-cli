"""CLI commands for quota management."""

from __future__ import annotations

from pathlib import Path

import click

from envchain.env_quota import (
    check_quota,
    get_quota,
    list_quotas,
    remove_quota,
    set_quota,
)


def register_quota_commands(cli: click.Group, get_store) -> None:
    cli.add_command(cmd_quota)

    @cmd_quota.command("set")
    @click.argument("profile")
    @click.argument("limit", type=int)
    @click.pass_context
    def _set(ctx, profile, limit):
        """Set the variable quota for PROFILE."""
        store_path = Path(get_store(ctx))
        try:
            result = set_quota(store_path, profile, limit)
            click.echo(result.message)
        except ValueError as exc:
            click.echo(f"Error: {exc}", err=True)
            ctx.exit(1)

    @cmd_quota.command("get")
    @click.argument("profile")
    @click.pass_context
    def _get(ctx, profile):
        """Show the quota limit for PROFILE."""
        store_path = Path(get_store(ctx))
        limit = get_quota(store_path, profile)
        if limit is None:
            click.echo(f"No quota set for '{profile}'.")
        else:
            click.echo(f"{profile}: {limit}")

    @cmd_quota.command("remove")
    @click.argument("profile")
    @click.pass_context
    def _remove(ctx, profile):
        """Remove the quota for PROFILE."""
        store_path = Path(get_store(ctx))
        if remove_quota(store_path, profile):
            click.echo(f"Quota for '{profile}' removed.")
        else:
            click.echo(f"No quota found for '{profile}'.")

    @cmd_quota.command("check")
    @click.argument("profile")
    @click.argument("count", type=int)
    @click.pass_context
    def _check(ctx, profile, count):
        """Check if COUNT variables is within the quota for PROFILE."""
        store_path = Path(get_store(ctx))
        result = check_quota(store_path, profile, count)
        click.echo(result.message)
        if not result.ok:
            ctx.exit(1)

    @cmd_quota.command("list")
    @click.pass_context
    def _list(ctx):
        """List all quotas."""
        store_path = Path(get_store(ctx))
        quotas = list_quotas(store_path)
        if not quotas:
            click.echo("No quotas configured.")
        else:
            for profile, limit in sorted(quotas.items()):
                click.echo(f"{profile}: {limit}")


@click.group("quota")
def cmd_quota():
    """Manage per-profile variable quotas."""
