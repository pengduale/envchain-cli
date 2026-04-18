"""CLI commands for passphrase rotation."""

from __future__ import annotations

import click

from envchain.cli import _get_store
from envchain.rotate import rotate_passphrase, rotate_single


def register_rotate_commands(cli: click.Group) -> None:
    cli.add_command(cmd_rotate)
    cli.add_command(cmd_rotate_one)


@click.command("rotate")
@click.option("--store", "store_path", default=".envchain.json", show_default=True)
@click.password_option("--old-passphrase", prompt="Old passphrase", confirmation_prompt=False)
@click.password_option("--new-passphrase", prompt="New passphrase")
def cmd_rotate(store_path: str, old_passphrase: str, new_passphrase: str) -> None:
    """Re-encrypt ALL variables with a new passphrase."""
    path = _get_store(store_path)
    try:
        count = rotate_passphrase(path, old_passphrase, new_passphrase)
        click.echo(f"Rotated {count} variable(s) successfully.")
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"Rotation failed: {exc}") from exc


@click.command("rotate-one")
@click.argument("variable")
@click.option("--store", "store_path", default=".envchain.json", show_default=True)
@click.password_option("--old-passphrase", prompt="Old passphrase", confirmation_prompt=False)
@click.password_option("--new-passphrase", prompt="New passphrase")
def cmd_rotate_one(variable: str, store_path: str, old_passphrase: str, new_passphrase: str) -> None:
    """Re-encrypt a single VARIABLE with a new passphrase."""
    path = _get_store(store_path)
    try:
        rotate_single(path, variable, old_passphrase, new_passphrase)
        click.echo(f"Variable '{variable}' rotated successfully.")
    except KeyError:
        raise click.ClickException(f"Variable '{variable}' not found in store.") from None
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    except Exception as exc:
        raise click.ClickException(f"Rotation failed: {exc}") from exc
