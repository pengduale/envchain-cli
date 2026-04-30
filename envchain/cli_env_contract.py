"""CLI commands for contract management."""

import click
from envchain.env_contract import (
    set_contract,
    get_contract,
    remove_contract,
    enforce_contract,
    list_contracts,
)


def register_contract_commands(cli, get_store):
    @cli.group("contract")
    def cmd_contract():
        """Manage variable contracts (type, pattern, length constraints)."""

    @cmd_contract.command("set")
    @click.argument("key")
    @click.option("--type", "value_type", default="string", show_default=True,
                  help="Expected type: string, integer, float, boolean.")
    @click.option("--pattern", default=None, help="Regex pattern the value must match.")
    @click.option("--min-length", type=int, default=None, help="Minimum value length.")
    @click.option("--max-length", type=int, default=None, help="Maximum value length.")
    @click.option("--optional", is_flag=True, default=False, help="Mark variable as optional.")
    @click.pass_context
    def cmd_contract_set(ctx, key, value_type, pattern, min_length, max_length, optional):
        """Set a contract for KEY."""
        store_path = get_store(ctx)
        result = set_contract(
            store_path, key,
            value_type=value_type,
            pattern=pattern,
            min_length=min_length,
            max_length=max_length,
            required=not optional,
        )
        if result.ok:
            click.echo(f"Contract set for '{key}'.")
        else:
            click.echo(f"Error: {result.message}", err=True)
            ctx.exit(1)

    @cmd_contract.command("get")
    @click.argument("key")
    @click.pass_context
    def cmd_contract_get(ctx, key):
        """Show contract for KEY."""
        store_path = get_store(ctx)
        contract = get_contract(store_path, key)
        if contract is None:
            click.echo(f"No contract defined for '{key}'.")
            return
        for field, val in contract.items():
            if val is not None:
                click.echo(f"  {field}: {val}")

    @cmd_contract.command("remove")
    @click.argument("key")
    @click.pass_context
    def cmd_contract_remove(ctx, key):
        """Remove contract for KEY."""
        store_path = get_store(ctx)
        removed = remove_contract(store_path, key)
        if removed:
            click.echo(f"Contract removed for '{key}'.")
        else:
            click.echo(f"No contract found for '{key}'.")

    @cmd_contract.command("enforce")
    @click.argument("key")
    @click.argument("value")
    @click.pass_context
    def cmd_contract_enforce(ctx, key, value):
        """Check VALUE against the contract for KEY."""
        store_path = get_store(ctx)
        result = enforce_contract(store_path, key, value)
        status = click.style("PASS", fg="green") if result.ok else click.style("FAIL", fg="red")
        click.echo(f"[{status}] {key}: {result.message}")
        if not result.ok:
            ctx.exit(1)

    @cmd_contract.command("list")
    @click.pass_context
    def cmd_contract_list(ctx):
        """List all contracts."""
        store_path = get_store(ctx)
        contracts = list_contracts(store_path)
        if not contracts:
            click.echo("No contracts defined.")
            return
        for key, spec in contracts.items():
            parts = [f"type={spec['type']}"]
            if spec.get("pattern"):
                parts.append(f"pattern={spec['pattern']}")
            if spec.get("min_length") is not None:
                parts.append(f"min={spec['min_length']}")
            if spec.get("max_length") is not None:
                parts.append(f"max={spec['max_length']}")
            parts.append("required" if spec.get("required") else "optional")
            click.echo(f"  {key}: {', '.join(parts)}")
