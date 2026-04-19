"""CLI commands for schema-based environment variable validation."""
import json
import click
from envchain.env_validate import load_schema, validate_all


def register_validate_commands(cli, get_store):
    @cli.group("validate")
    def cmd_validate():
        """Validate stored variables against a schema."""

    @cmd_validate.command("run")
    @click.argument("schema_file", type=click.Path(exists=True))
    @click.option("--passphrase", "-p", prompt=True, hide_input=True)
    @click.option("--fail-fast", is_flag=True, default=False)
    @click.pass_context
    def cmd_validate_run(ctx, schema_file, passphrase, fail_fast):
        """Run validation rules from a JSON schema file."""
        store_path = get_store(ctx)
        with open(schema_file) as f:
            raw = json.load(f)
        rules = load_schema(raw)
        results = validate_all(store_path, passphrase, rules)

        passed = 0
        failed = 0
        for r in results:
            status = click.style("PASS", fg="green") if r.passed else click.style("FAIL", fg="red")
            click.echo(f"  [{status}] {r.key}: {r.message}")
            if r.passed:
                passed += 1
            else:
                failed += 1
                if fail_fast:
                    raise click.ClickException(f"Validation failed on key '{r.key}'")

        click.echo(f"\n{passed} passed, {failed} failed.")
        if failed:
            ctx.exit(1)

    @cmd_validate.command("check")
    @click.argument("key")
    @click.option("--passphrase", "-p", prompt=True, hide_input=True)
    @click.option("--pattern", default=None)
    @click.option("--min-length", default=0, type=int)
    @click.option("--required/--optional", default=True)
    @click.pass_context
    def cmd_validate_check(ctx, key, passphrase, pattern, min_length, required):
        """Quick inline validation of a single key."""
        from envchain.env_validate import ValidationRule, validate_variable
        store_path = get_store(ctx)
        rule = ValidationRule(key=key, required=required, pattern=pattern, min_length=min_length)
        result = validate_variable(store_path, passphrase, rule)
        status = click.style("PASS", fg="green") if result.passed else click.style("FAIL", fg="red")
        click.echo(f"[{status}] {result.key}: {result.message}")
        if not result.passed:
            ctx.exit(1)
