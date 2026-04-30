"""CLI commands for approval workflow management."""

import click
from envchain.env_approval import (
    set_approval, get_approval, remove_approval, list_approvals, VALID_STATUSES
)


def register_approval_commands(cli, get_store):
    @cli.group("approval")
    def cmd_approval():
        """Manage variable approval workflows."""

    @cmd_approval.command("set")
    @click.argument("key")
    @click.argument("status", type=click.Choice(sorted(VALID_STATUSES)))
    @click.option("--approver", default=None, help="Name or ID of the approver.")
    @click.option("--message", default=None, help="Optional approval note.")
    @click.pass_context
    def cmd_approval_set(ctx, key, status, approver, message):
        """Set the approval status for a variable."""
        store_path = get_store(ctx)
        result = set_approval(store_path, key, status, approver=approver, message=message)
        if not result.ok:
            click.echo(f"Error: {result.message}", err=True)
            ctx.exit(1)
        else:
            click.echo(f"[{result.status.upper()}] {key}" + (f" (by {approver})" if approver else ""))

    @cmd_approval.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_approval_get(ctx, key):
        """Get the approval status for a variable."""
        store_path = get_store(ctx)
        result = get_approval(store_path, key)
        if result is None:
            click.echo(f"No approval record for '{key}'.", err=True)
            ctx.exit(1)
        else:
            approver_str = f", approver={result.approver}" if result.approver else ""
            click.echo(f"{key}: {result.status}{approver_str}")
            if result.message:
                click.echo(f"  Note: {result.message}")

    @cmd_approval.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_approval_remove(ctx, key):
        """Remove the approval record for a variable."""
        store_path = get_store(ctx)
        removed = remove_approval(store_path, key)
        if removed:
            click.echo(f"Removed approval record for '{key}'.")
        else:
            click.echo(f"No approval record found for '{key}'.", err=True)
            ctx.exit(1)

    @cmd_approval.command("list")
    @click.option("--status", default=None, type=click.Choice(sorted(VALID_STATUSES)),
                  help="Filter by status.")
    @click.pass_context
    def cmd_approval_list(ctx, status):
        """List all approval records, optionally filtered by status."""
        store_path = get_store(ctx)
        records = list_approvals(store_path, status_filter=status)
        if not records:
            click.echo("No approval records found.")
            return
        for r in records:
            approver_str = f" (by {r.approver})" if r.approver else ""
            click.echo(f"  [{r.status.upper()}] {r.key}{approver_str}")
