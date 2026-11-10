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

resource "azurerm_storage_account" "datalake" {
  name                      = "${var.prefix}${var.environment}dl${var.suffix}"
  location                  = var.location
  resource_group_name       = var.resource_group_name
  account_tier              = "Standard"
  account_replication_type  = "ZRS"
  is_hns_enabled            = true
  enable_https_traffic_only = true
  min_tls_version           = "TLS1_2"

  blob_properties {
    container_delete_retention_policy {
      days = 7
    }
  }

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    private_link_access = [
      {
        endpoint_resource_id = var.resource_group_name
      }
    ]
  }

  tags = var.tags
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "tmp" {
  name                  = "tmp"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_role_assignment" "storage_contributor" {
  scope                = azurerm_storage_account.datalake.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = var.resource_group_name
}

resource "azurerm_storage_account_network_rules" "datalake" {
  storage_account_id = azurerm_storage_account.datalake.id

  default_action             = "Allow"
  private_link_access = [
    {
      endpoint_resource_id = var.resource_group_name
    }
  ]
}

output "account_name" {
  description = "Storage account name"
  value       = azurerm_storage_account.datalake.name
}

output "account_id" {
  description = "Storage account ID"
  value       = azurerm_storage_account.datalake.id
}

output "primary_blob_endpoint" {
  description = "Primary blob endpoint"
  value       = azurerm_storage_account.datalake.primary_blob_endpoint
}

output "bronze_container_name" {
  description = "Bronze container name"
  value       = azurerm_storage_container.bronze.name
}

output "silver_container_name" {
  description = "Silver container name"
  value       = azurerm_storage_container.silver.name
}

output "gold_container_name" {
  description = "Gold container name"
  value       = azurerm_storage_container.gold.name
}
