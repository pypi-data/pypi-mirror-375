"""Command-line interface for Lock & Key."""

import click

from lock_and_key.core import LockAndKeyScanner


@click.group()
def cli():
    """Lock & Key Cloud Scanner CLI."""
    pass


@cli.command()
@click.option("--output-dir", type=str, default="./reports", help="Output directory for reports")
def interactive(output_dir):
    """Run the interactive cloud scan workflow."""
    scanner = LockAndKeyScanner(output_dir=output_dir)
    scanner.run_interactive()


@cli.command()
@click.option(
    "--provider",
    type=click.Choice(["AWS", "GCP", "Azure"]),
    required=True,
    help="Cloud provider to scan",
)
@click.option("--profile", type=str, help="AWS profile name")
@click.option("--access-key", type=str, help="AWS Access Key ID")
@click.option("--secret-key", type=str, help="AWS Secret Access Key")
@click.option("--region", type=str, help="AWS Region")
@click.option("--creds-path", type=str, help="Path to credentials file (GCP/Azure)")
@click.option("--creds-json", type=str, help="GCP credentials JSON")
@click.option("--client-id", type=str, help="Azure Client ID")
@click.option("--secret", type=str, help="Azure Client Secret")
@click.option("--tenant-id", type=str, help="Azure Tenant ID")
@click.option("--subscription-id", type=str, help="Azure Subscription ID")
@click.option("--output-dir", type=str, default="./reports", help="Output directory for reports")
def scan(provider, output_dir, **kwargs):
    """Run a single provider scan with provided credentials."""
    scanner = LockAndKeyScanner(output_dir=output_dir)
    scanner.run_single_provider(provider, **kwargs)


if __name__ == "__main__":
    cli()
