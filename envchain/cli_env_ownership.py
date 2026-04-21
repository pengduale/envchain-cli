"""CLI commands for env variable ownership management."""
import click
from envchain.env_ownership import set_ownership, get_ownership, remove_ownership, list_owned_by, list_owned_by_team


def register_ownership_commands(cli, get_store):
    @cli.group("ownership")
    def cmd_ownership():
        """Manage ownership of environment variables."""

    @cmd_ownership.command("set")
    @click.argument("key")
    @click.argument("owner")
    @click.option("--team", default=None, help="Team responsible for this variable")
    @click.pass_context
    def cmd_ownership_set(ctx, key, owner, team):
        """Assign an owner (and optional team) to a variable."""
        store_path = get_store(ctx)
        result = set_ownership(store_path, key, owner, team)
        if result.ok:
            msg = f"Owner of '{key}' set to '{owner}'"
            if team:
                msg += f" (team: {team})"
            click.echo(msg)
        else:
            click.echo(f"Error: {result.message}", err=True)
            ctx.exit(1)

    @cmd_ownership.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_ownership_get(ctx, key):
        """Show ownership info for a variable."""
        store_path = get_store(ctx)
        result = get_ownership(store_path, key)
        if result is None:
            click.echo(f"No ownership record for '{key}'")
        else:
            line = f"{key}: owner={result.owner}"
            if result.team:
                line += f", team={result.team}"
            click.echo(line)

    @cmd_ownership.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_ownership_remove(ctx, key):
        """Remove ownership record for a variable."""
        store_path = get_store(ctx)
        removed = remove_ownership(store_path, key)
        if removed:
            click.echo(f"Ownership record for '{key}' removed.")
        else:
            click.echo(f"No ownership record found for '{key}'.")

    @cmd_ownership.command("list")
    @click.option("--owner", default=None, help="Filter by owner name")
    @click.option("--team", default=None, help="Filter by team name")
    @click.pass_context
    def cmd_ownership_list(ctx, owner, team):
        """List variables filtered by owner or team."""
        store_path = get_store(ctx)
        if owner:
            keys = list_owned_by(store_path, owner)
            label = f"owner '{owner}'"
        elif team:
            keys = list_owned_by_team(store_path, team)
            label = f"team '{team}'"
        else:
            click.echo("Provide --owner or --team to filter.", err=True)
            ctx.exit(1)
            return
        if not keys:
            click.echo(f"No variables found for {label}.")
        else:
            click.echo(f"Variables for {label}:")
            for k in keys:
                click.echo(f"  {k}")
