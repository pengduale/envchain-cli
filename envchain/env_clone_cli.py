import click
from envchain.env_clone import clone_profile


def register_clone_commands(cli, get_store):
    @cli.group("clone")
    def cmd_clone():
        """Clone profile variables."""

    @cmd_clone.command("run")
    @click.argument("source")
    @click.argument("dest")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.option("--keys", multiple=True, help="Limit to specific keys")
    @click.pass_context
    def cmd_clone_run(ctx, source, dest, overwrite, keys):
        """Clone SOURCE profile into DEST profile."""
        store = get_store(ctx)
        passphrase = ctx.obj["passphrase"]

        if source == dest:
            raise click.UsageError("SOURCE and DEST profiles must be different.")

        key_filter = list(keys) if keys else None
        results = clone_profile(
            store, passphrase, source, dest,
            overwrite=overwrite, keys=key_filter
        )
        copied = [r for r in results if r.copied]
        skipped = [r for r in results if not r.copied]
        for r in copied:
            click.echo(f"  cloned: {r.key}")
        for r in skipped:
            click.echo(f"  skipped: {r.key} ({r.reason})")
        click.echo(f"Done: {len(copied)} cloned, {len(skipped)} skipped.")
