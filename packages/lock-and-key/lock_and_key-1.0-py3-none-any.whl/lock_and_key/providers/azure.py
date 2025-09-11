"""Azure provider implementation."""

import click

from lock_and_key.types import AzureCreds, CloudProviderBase


class AzureProvider(CloudProviderBase):
    """Azure cloud provider implementation."""

    name = "Azure"
    description = "Microsoft Azure"

    def prompt_creds(self) -> AzureCreds:
        """Prompt for Azure credentials."""
        creds_path = click.prompt(
            "Enter path to Azure credentials file (leave blank to enter manually)",
            default="",
            show_default=False,
        )
        if creds_path:
            return AzureCreds(creds_path=creds_path)

        client_id = click.prompt("Enter Azure Client ID")
        secret = click.prompt("Enter Azure Client Secret", hide_input=True)
        tenant_id = click.prompt("Enter Azure Tenant ID")
        subscription_id = click.prompt("Enter Azure Subscription ID")

        return AzureCreds(
            client_id=client_id,
            secret=secret,
            tenant_id=tenant_id,
            subscription_id=subscription_id,
        )
