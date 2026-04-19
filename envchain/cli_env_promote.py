"""CLI commands for promoting variables between profiles."""

import click
from envchain.env_promote import promote_all, promote_variable


def register_promote_commands(cli, get_store):
    @cli.group("promote")
    def cmd_promote():
        """Promote variables between profiles."""

    @cmd_promote.command("run")
    @click.argument("source")
    @click.argument("target")
    @click.option("--key", "-k", multiple=True, help="Specific keys to promote (default: all)")
    @click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys in target")
    @click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
    @click.pass_context
    def cmd_promote_run(ctx, source, target, key, overwrite, passphrase):
        """Promote variables from SOURCE profile to TARGET profile."""
        store_path = get_store(ctx)
        keys = list(key) if key else None
        results = promote_all(store_path, source, target, passphrase, overwrite=overwrite, keys=keys)

        if not results:
            click.echo("No variables found in source profile.")
            return

        for r in results:
            if r.skipped:
                click.echo(f"  skip  {r.key} ({r.reason})")
            else:
                click.echo(f"  ok    {r.key}")

        promoted = sum(1 for r in results if not r.skipped)
        click.echo(f"\nPromoted {promoted}/{len(results)} variable(s) from '{source}' to '{target}'.")

    @cmd_promote.command("one")
    @click.argument("key")
    @click.argument("source")
    @click.argument("target")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
    @click.pass_context
    def cmd_promote_one(ctx, key, source, target, overwrite, passphrase):
        """Promote a single KEY from SOURCE to TARGET profile."""
        store_path = get_store(ctx)
        result = promote_variable(store_path, key, source, target, passphrase, overwrite)
        if result.skipped:
            click.echo(f"Skipped '{key}': {result.reason}")
        else:
            click.echo(f"Promoted '{key}' from '{source}' to '{target}'.")
