"""CLI commands for env scope management."""
import click
from envchain.env_scope import set_scope, get_scope, remove_scope, list_scopes


def register_scope_commands(cli, get_store):
    @cli.group("scope")
    def cmd_scope():
        """Manage variable scopes."""

    @cmd_scope.command("set")
    @click.argument("scope")
    @click.argument("keys", nargs=-1, required=True)
    @click.pass_context
    def cmd_scope_set(ctx, scope, keys):
        """Assign KEYS to a named SCOPE."""
        store_dir, _ = get_store(ctx)
        result = set_scope(store_dir, scope, list(keys))
        click.echo(f"Scope '{result.scope}' set with keys: {', '.join(result.keys)}")

    @cmd_scope.command("get")
    @click.argument("scope")
    @click.pass_context
    def cmd_scope_get(ctx, scope):
        """List keys in a SCOPE."""
        store_dir, _ = get_store(ctx)
        keys = get_scope(store_dir, scope)
        if keys is None:
            click.echo(f"Scope '{scope}' not found.", err=True)
            ctx.exit(1)
        else:
            for k in keys:
                click.echo(k)

    @cmd_scope.command("remove")
    @click.argument("scope")
    @click.pass_context
    def cmd_scope_remove(ctx, scope):
        """Remove a SCOPE definition."""
        store_dir, _ = get_store(ctx)
        removed = remove_scope(store_dir, scope)
        if removed:
            click.echo(f"Scope '{scope}' removed.")
        else:
            click.echo(f"Scope '{scope}' not found.", err=True)
            ctx.exit(1)

    @cmd_scope.command("list")
    @click.pass_context
    def cmd_scope_list(ctx):
        """List all scopes."""
        store_dir, _ = get_store(ctx)
        scopes = list_scopes(store_dir)
        if not scopes:
            click.echo("No scopes defined.")
        for name, keys in scopes.items():
            click.echo(f"{name}: {', '.join(keys)}")
