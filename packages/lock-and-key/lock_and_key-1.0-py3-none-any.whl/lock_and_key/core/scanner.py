"""Core scanner functionality."""

from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from lock_and_key.core.ui import print_banner
from lock_and_key.providers import PROVIDER_CLASSES
from lock_and_key.types import AWSCreds, AzureCreds, GCPCreds, ScanSummary


class LockAndKeyScanner:
    """Main scanner class for Lock & Key."""

    def __init__(self, output_dir: str = "./reports"):
        self.providers = PROVIDER_CLASSES
        self.summary = ScanSummary()
        self.console = Console()
        self.output_dir = output_dir

    def select_cloud_provider(self) -> Optional[str]:
        """Prompt user to select a cloud provider."""
        provider_names = list(self.providers.keys())
        for idx, name in enumerate(provider_names, 1):
            self.console.print(f"[cyan]{idx}.[/cyan] {name} ({self.providers[name].description})")

        choice = click.prompt("Select a provider by number", type=int)
        if 1 <= choice <= len(provider_names):
            return provider_names[choice - 1]
        return None

    def run_interactive(self) -> None:
        """Run interactive scanning workflow."""
        print_banner()

        # Prompt for output directory if not set via CLI
        if self.output_dir == "./reports":
            self.output_dir = click.prompt("Enter output directory for reports", default="./reports")

        while True:
            provider_name = self.select_cloud_provider()
            if not provider_name:
                self.console.print("[red]Invalid selection. Exiting.[/red]")
                break

            provider_cls = self.providers[provider_name]
            provider = provider_cls()
            creds = provider.prompt_creds()

            # Confirm before scanning
            if not click.confirm(f"Proceed with {provider_name} scan?", default=True):
                self.console.print("[yellow]Scan cancelled.[/yellow]")
                continue

            # Run scan with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task(f"Scanning {provider_name}...", total=None)
                result = provider.run_analysis(creds, output_dir=self.output_dir)
                progress.update(task, completed=True)
            self.summary.add_result(result)

            again = click.confirm("Would you like to scan another cloud provider?", default=False)
            if not again:
                break

        self.summary.render()
        self.console.print("[bold cyan]Thank you for using Lock & Key Cloud Scanner![/bold cyan]")

    def run_single_provider(self, provider_name: str, **kwargs: dict[str, object]) -> None:
        """Run scan for a single provider with provided credentials."""
        print_banner()

        provider_cls = self.providers.get(provider_name)
        if not provider_cls:
            self.console.print(f"[red]Unknown provider: {provider_name}[/red]")
            return

        provider = provider_cls()
        creds = self._build_credentials(provider_name, **kwargs)
        if not creds:
            self.console.print("[red]Invalid credentials provided.[/red]")
            return

        # Confirm before scanning
        if not click.confirm(f"Proceed with {provider_name} scan?", default=True):
            self.console.print("[yellow]Scan cancelled.[/yellow]")
            return

        # Run scan with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"Scanning {provider_name}...", total=None)
            result = provider.run_analysis(creds, output_dir=self.output_dir)
            progress.update(task, completed=True)
        self.summary.add_result(result)
        self.summary.render()
        self.console.print("[bold cyan]Thank you for using Lock & Key Cloud Scanner![/bold cyan]")

    def _build_credentials(self, provider_name: str, **kwargs):
        """Build credentials object from kwargs."""
        if provider_name == "AWS":
            return AWSCreds(
                profile=kwargs.get("profile"),
                access_key=kwargs.get("access_key"),
                secret_key=kwargs.get("secret_key"),
                region=kwargs.get("region"),
            )
        elif provider_name == "GCP":
            return GCPCreds(creds_path=kwargs.get("creds_path"), creds_json=kwargs.get("creds_json"))
        elif provider_name == "Azure":
            return AzureCreds(
                creds_path=kwargs.get("creds_path"),
                client_id=kwargs.get("client_id"),
                secret=kwargs.get("secret"),
                tenant_id=kwargs.get("tenant_id"),
                subscription_id=kwargs.get("subscription_id"),
            )
        return None
