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

variable "subnet_id" {
  description = "Databricks subnet ID"
  type        = string
}

variable "vnet_id" {
  description = "Virtual Network ID"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault ID for secret storage"
  type        = string
}

resource "azurerm_databricks_workspace" "main" {
  name                        = "${var.prefix}-${var.environment}-dbw-${var.suffix}"
  location                    = var.location
  resource_group_name         = var.resource_group_name
  sku                         = "premium"
  managed_resource_group_name = "${var.prefix}-${var.environment}-dbw-managed-${var.suffix}"

  custom_parameters {
    virtual_network_id  = var.vnet_id
    databricks_subnet_id = var.subnet_id
    databricksSubnetCustomerSubnetName = "databricks"

    no_public_ip        = true

    secret_scope_name   = "${var.prefix}-${var.environment}-scope"

    key_vault_id        = var.key_vault_id
  }

  tags = var.tags
}

resource "databricks_mws_networking" "vnet_connection" {
  provider           = databricks
  account_id         = var.environment
  workspace_id       = azurerm_databricks_workspace.main.id
  vnet_id            = var.vnet_id
  subnet_id          = var.subnet_id
  private_dns_zone_id = azurerm_private_dns_zone.databricks.id
}

resource "azurerm_private_dns_zone" "databricks" {
  name                = "privatelink.azuredatabricks.net"
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "databricks" {
  name                  = "${var.prefix}-${var.environment}-vnet-link-${var.suffix}"
  private_dns_zone_name = azurerm_private_dns_zone.databricks.name
  virtual_network_id    = var.vnet_id
  registration_enabled  = false
}

output "workspace_id" {
  description = "Databricks workspace ID"
  value       = azurerm_databricks_workspace.main.workspace_id
}

output "workspace_url" {
  description = "Databricks workspace URL"
  value       = azurerm_databricks_workspace.main.workspace_url
}

output "managed_resource_group_id" {
  description = "Managed resource group ID"
  value       = azurerm_databricks_workspace.main.managed_resource_group_id
}
