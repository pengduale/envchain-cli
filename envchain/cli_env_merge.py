"""CLI commands for merging profiles."""
import click
from envchain.env_merge import merge_profiles, merge_summary


def register_merge_commands(cli, get_store):
    @cli.group("merge")
    def cmd_merge():
        """Merge variables across profiles."""

    @cmd_merge.command("run")
    @click.argument("sources", nargs=-1, required=True)
    @click.option("--target", required=True, help="Target profile name.")
    @click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
    @click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing keys.")
    @click.option("--key", "keys", multiple=True, help="Limit to specific keys.")
    @click.pass_context
    def cmd_merge_run(ctx, sources, target, passphrase, overwrite, keys):
        """Merge SOURCE profiles into TARGET profile."""
        store_path = get_store(ctx)
        results = merge_profiles(
            store_path,
            list(sources),
            target,
            passphrase,
            overwrite=overwrite,
            keys=list(keys) if keys else None,
        )
        if not results:
            click.echo("Nothing to merge.")
            return
        for r in results:
            icon = {"copied": "+", "skipped": "=", "overwritten": "~"}.get(r.status, "?")
            click.echo(f"  [{icon}] {r.key}  ({r.source_profile} -> {r.target_profile})")
        s = merge_summary(results)
        click.echo(f"\nDone: {s['copied']} copied, {s['overwritten']} overwritten, {s['skipped']} skipped.")

    @cmd_merge.command("summary")
    @click.argument("sources", nargs=-1, required=True)
    @click.option("--target", required=True)
    @click.option("--passphrase", envvar="ENVCHAIN_PASSPHRASE", prompt=True, hide_input=True)
    @click.pass_context
    def cmd_merge_summary(ctx, sources, target, passphrase):
        """Show a dry-run summary of what would be merged."""
        store_path = get_store(ctx)
        results = merge_profiles(store_path, list(sources), target, passphrase, overwrite=False)
        s = merge_summary(results)
        click.echo(f"Would copy {s['copied']}, skip {s['skipped']} existing keys.")
