"""Azure authentication utilities.

Uses Azure Managed Identity for authentication - no personal tokens.
Supports service-to-service authentication via Microsoft Entra ID.
"""

from __future__ import annotations

import os
from typing import Optional

from azure.identity import (
    AzureCliCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
    WorkloadIdentityCredential,
)


def get_credential() -> DefaultAzureCredential:
    """Get appropriate Azure credential based on environment.

    Priority:
    1. Workload Identity (Kubernetes)
    2. Managed Identity (Azure resources)
    3. Azure CLI (local development)

    Returns:
        DefaultAzureCredential configured for the environment
    """
    if os.environ.get("KIOBEL_SERVICE_ACCOUNT_TOKEN"):
        return WorkloadIdentityCredential()

    if os.environ.get("IDENTITY_ENDPOINT"):
        return ManagedIdentityCredential()

    if os.environ.get("AZURE_CLI_TOKEN"):
        return AzureCliCredential()

    return DefaultAzureCredential()


def get_storage_account_key(
    credential: DefaultAzureCredential,
    subscription_id: str,
    resource_group: str,
    account_name: str,
) -> str:
    """Get storage account access key from Azure Key Vault.

    The storage account key should be stored in Key Vault, not retrieved
    directly. This function demonstrates the pattern.

    Args:
        credential: Azure credential
        subscription_id: Azure subscription ID
        resource_group: Resource group name
        account_name: Storage account name

    Returns:
        Storage account key (should come from Key Vault in production)
    """
    from azure.keyvault.secrets import SecretClient
    from azure.mgmt.storage import StorageManagementClient

    key_vault_url = os.environ.get("KEY_VAULT_URL")
    if not key_vault_url:
        raise EnvironmentError("KEY_VAULT_URL not configured")

    vault_credential = get_credential()
    vault_client = SecretClient(vault_url=key_vault_url, credential=vault_credential)

    storage_client = StorageManagementClient(
        credential=vault_credential,
        subscription_id=subscription_id,
    )

    keys = storage_client.storage_accounts.list_keys(
        resource_group_name=resource_group,
        account_name=account_name,
    )

    key = keys.keys[0].value
    secret_name = f"storage-{account_name}-key"

    return vault_client.set_secret(secret_name, key).value


def get_databricks_token(
    aad_token: Optional[str] = None,
    workspace_url: Optional[str] = None,
) -> str:
    """Get Databricks access token using Azure AD token.

    Args:
        aad_token: Optional Azure AD token (will acquire if not provided)
        workspace_url: Databricks workspace URL

    Returns:
        Databricks personal access token
    """
    if not workspace_url:
        workspace_url = os.environ.get("DATABRICKS_WORKSPACE_URL")

    if not workspace_url:
        raise EnvironmentError("DATABRICKS_WORKSPACE_URL not configured")

    if not aad_token:
        credential = get_credential()
        aad_token = credential.get_token(
            "2ff814a6-3304-4ab8-85cb-cd0e6f844c6e/.default"
        ).token

    return f"Bearer {aad_token}"
