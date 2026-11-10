variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "prefix" {
  description = "Resource name prefix"
  type        = string
}

variable "suffix" {
  description = "Resource name suffix"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
}

variable "storage_account_id" {
  description = "Storage account ID for secret store"
  type        = string
}

resource "azurerm_key_vault" "main" {
  name                        = "${var.prefix}-${var.environment}-kv-${var.suffix}"
  location                    = var.location
  resource_group_name         = var.resource_group_name
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"
  soft_delete_retention_days  = 7
  purge_protection_enabled    = var.environment == "prod" ? true : false

  enable_rbac_authorization = true

  network_acls {
    default_action = "Allow"
    bypass         = "AzureServices"
  }

  tags = var.tags
}

data "azurerm_client_config" "current" {}

resource "azurerm_role_assignment" "key_vault_admin" {
  scope                = azurerm_key_vault.main.id
  role_definition_name = "Key Vault Secrets Officer"
  principal_id         = data.azurerm_client_config.current.object_id
}

resource "azurerm_role_assignment" "storage_key_reader" {
  scope                = var.storage_account_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_key_vault.main.id
}

output "id" {
  description = "Key Vault ID"
  value       = azurerm_key_vault.main.id
}

output "vault_url" {
  description = "Key Vault URL"
  value       = azurerm_key_vault.main.vault_uri
}

output "name" {
  description = "Key Vault name"
  value       = azurerm_key_vault.main.name
}
