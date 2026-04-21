"""CLI commands for per-key permission management."""
import click
from envchain.env_permission import (
    set_permissions,
    get_permissions,
    remove_permissions,
    has_permission,
    list_permissions,
)


def register_permission_commands(cli, get_store):
    @cli.group("permission")
    def cmd_permission():
        """Manage per-key access permissions."""

    @cmd_permission.command("set")
    @click.argument("key")
    @click.argument("permissions", nargs=-1, required=True)
    @click.pass_context
    def cmd_permission_set(ctx, key, permissions):
        """Set permissions for KEY (read, write, delete)."""
        store_path = get_store(ctx)
        try:
            result = set_permissions(store_path, key, list(permissions))
            click.echo(f"Set permissions for '{key}': {', '.join(result.permissions)}")
        except ValueError as e:
            raise click.ClickException(str(e))

    @cmd_permission.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_permission_get(ctx, key):
        """Get permissions for KEY."""
        store_path = get_store(ctx)
        perms = get_permissions(store_path, key)
        if perms is None:
            click.echo(f"No restrictions set for '{key}' (all permissions allowed).")
        else:
            click.echo(f"{key}: {', '.join(perms)}")

    @cmd_permission.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_permission_remove(ctx, key):
        """Remove permission restrictions for KEY."""
        store_path = get_store(ctx)
        removed = remove_permissions(store_path, key)
        if removed:
            click.echo(f"Removed permissions for '{key}'.")
        else:
            click.echo(f"No permissions found for '{key}'.")

    @cmd_permission.command("check")
    @click.argument("key")
    @click.argument("permission")
    @click.pass_context
    def cmd_permission_check(ctx, key, permission):
        """Check if KEY has PERMISSION."""
        store_path = get_store(ctx)
        allowed = has_permission(store_path, key, permission)
        status = "allowed" if allowed else "denied"
        click.echo(f"'{permission}' on '{key}': {status}")

    @cmd_permission.command("list")
    @click.pass_context
    def cmd_permission_list(ctx):
        """List all key permission restrictions."""
        store_path = get_store(ctx)
        all_perms = list_permissions(store_path)
        if not all_perms:
            click.echo("No permission restrictions defined.")
            return
        for key, perms in sorted(all_perms.items()):
            click.echo(f"  {key}: {', '.join(perms)}")
