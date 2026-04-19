"""CLI commands for running subprocesses with injected env vars."""
import sys
import click

from envchain.cli import _get_store
from envchain.env_run import run_command


def register_env_run_commands(cli):
    cli.add_command(cmd_run)


@click.command("run")
@click.option("--store", "store_path", default=None, help="Path to store file.")
@click.option("--passphrase", prompt=True, hide_input=True, help="Encryption passphrase.")
@click.option("--profile", default=None, help="Profile to load variables from.")
@click.option(
    "--env", "-e", "extra_env", multiple=True, metavar="KEY=VALUE",
    help="Additional KEY=VALUE pairs to inject (not stored).",
)
@click.argument("command", nargs=-1, required=True)
def cmd_run(store_path, passphrase, profile, extra_env, command):
    """Run COMMAND with decrypted env vars injected."""
    store = _get_store(store_path)

    extra = {}
    for pair in extra_env:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair}")
        k, v = pair.split("=", 1)
        extra[k] = v

    try:
        exit_code = run_command(
            list(command),
            store,
            passphrase,
            profile=profile,
            extra=extra or None,
        )
    except FileNotFoundError:
        raise click.ClickException(f"Command not found: {command[0]}")
    except Exception as exc:
        raise click.ClickException(str(exc))

    sys.exit(exit_code)
