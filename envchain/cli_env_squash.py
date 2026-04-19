import click
from envchain.env_squash import squash_profiles


def register_squash_commands(cli, get_store):
    @cli.group("squash")
    def cmd_squash():
        """Squash multiple profiles into one."""

    @cmd_squash.command("run")
    @click.argument("profiles", nargs=-1, required=True)
    @click.option("--dest", default="default", show_default=True, help="Destination profile")
    @click.option("--overwrite", is_flag=True, default=False)
    @click.pass_context
    def cmd_squash_run(ctx, profiles, dest, overwrite):
        """Squash PROFILES into DEST profile."""
        store = get_store(ctx)
        passphrase = ctx.obj["passphrase"]
        results = squash_profiles(
            store, passphrase, list(profiles),
            dest=dest, overwrite=overwrite
        )
        written = [r for r in results if r.written]
        skipped = [r for r in results if not r.written]
        for r in written:
            click.echo(f"  wrote [{r.source_profile}] {r.key} -> {dest}")
        for r in skipped:
            click.echo(f"  skipped [{r.source_profile}] {r.key}: {r.reason}")
        click.echo(f"Done: {len(written)} written, {len(skipped)} skipped.")
