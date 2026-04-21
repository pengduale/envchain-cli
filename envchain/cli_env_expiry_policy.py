"""CLI commands for managing expiry policies on envchain variables."""

import click

from envchain.env_expiry_policy import (
    get_expiry_policy,
    list_expiry_policies,
    remove_expiry_policy,
    set_expiry_policy,
)


def register_expiry_policy_commands(cli: click.Group, get_store) -> None:
    @cli.group("expiry-policy")
    def cmd_expiry_policy():
        """Manage expiry policies for stored variables."""

    @cmd_expiry_policy.command("set")
    @click.argument("key")
    @click.option("--max-age", required=True, type=int, help="Max age in days before expiry.")
    @click.option("--warn-before", default=3, show_default=True, type=int, help="Days before expiry to warn.")
    @click.option(
        "--action",
        default="warn",
        show_default=True,
        type=click.Choice(["warn", "delete", "lock"]),
        help="Action to take on expiry.",
    )
    @click.pass_context
    def cmd_set(ctx, key, max_age, warn_before, action):
        """Set an expiry policy for KEY."""
        store_path = get_store(ctx)
        try:
            result = set_expiry_policy(store_path, key, max_age, warn_before, action)
            click.echo(result.message)
        except ValueError as exc:
            raise click.ClickException(str(exc))

    @cmd_expiry_policy.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_get(ctx, key):
        """Show the expiry policy for KEY."""
        store_path = get_store(ctx)
        policy = get_expiry_policy(store_path, key)
        if policy is None:
            raise click.ClickException(f"No expiry policy found for {key!r}.")
        click.echo(f"key:            {key}")
        click.echo(f"max_age_days:   {policy['max_age_days']}")
        click.echo(f"warn_before:    {policy['warn_before_days']}")
        click.echo(f"action:         {policy['action']}")

    @cmd_expiry_policy.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_remove(ctx, key):
        """Remove the expiry policy for KEY."""
        store_path = get_store(ctx)
        removed = remove_expiry_policy(store_path, key)
        if removed:
            click.echo(f"Expiry policy for {key!r} removed.")
        else:
            raise click.ClickException(f"No expiry policy found for {key!r}.")

    @cmd_expiry_policy.command("list")
    @click.pass_context
    def cmd_list(ctx):
        """List all expiry policies."""
        store_path = get_store(ctx)
        policies = list_expiry_policies(store_path)
        if not policies:
            click.echo("No expiry policies defined.")
            return
        for key, policy in sorted(policies.items()):
            click.echo(
                f"{key}: max_age={policy['max_age_days']}d  "
                f"warn={policy['warn_before_days']}d  action={policy['action']}"
            )
