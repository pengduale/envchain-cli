"""CLI commands for comparing live env vs stored envchain values."""
import click
from envchain.env_diff_check import diff_live_vs_stored, summary


def register_env_diff_check_commands(cli, get_store):
    @cli.group("env-diff")
    def cmd_env_diff():
        """Compare live environment variables with stored values."""

    @cmd_env_diff.command("run")
    @click.option("--keys", "-k", multiple=True, help="Limit to specific keys.")
    @click.option("--live-only", is_flag=True, help="Include vars only in live env.")
    @click.option("--mismatches-only", is_flag=True, help="Show only mismatches.")
    @click.pass_context
    def cmd_diff_run(ctx, keys, live_only, mismatches_only):
        """Run a diff between stored and live environment."""
        store_path, passphrase = get_store(ctx)
        entries = diff_live_vs_stored(
            store_path,
            passphrase,
            keys=list(keys) if keys else None,
            include_live_only=live_only,
        )
        if mismatches_only:
            entries = [e for e in entries if e.status != "match"]

        if not entries:
            click.echo("No differences found.")
            return

        status_symbol = {
            "match": click.style("=", fg="green"),
            "mismatch": click.style("~", fg="yellow"),
            "stored_only": click.style("-", fg="red"),
            "live_only": click.style("+", fg="cyan"),
        }
        for e in entries:
            sym = status_symbol.get(e.status, "?")
            click.echo(f"  {sym} {e.key}  [{e.status}]")

    @cmd_env_diff.command("summary")
    @click.pass_context
    def cmd_diff_summary(ctx):
        """Print a summary count of diff statuses."""
        store_path, passphrase = get_store(ctx)
        entries = diff_live_vs_stored(store_path, passphrase)
        counts = summary(entries)
        for status, count in counts.items():
            click.echo(f"  {status}: {count}")
