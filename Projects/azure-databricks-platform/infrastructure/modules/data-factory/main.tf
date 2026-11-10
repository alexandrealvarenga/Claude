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

variable "databricks_workspace_id" {
  description = "Databricks workspace ID"
  type        = string
}

variable "storage_account_id" {
  description = "Storage account ID"
  type        = string
}

variable "key_vault_id" {
  description = "Key Vault ID"
  type        = string
}

resource "azurerm_data_factory" "main" {
  name                = "${var.prefix}-${var.environment}-adf-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku_name            = var.environment == "prod" ? "Standard" : "Basic"
  tags                = var.tags

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "adf_storage_access" {
  scope                = var.storage_account_id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_data_factory.main.identity[0].principal_id
}

resource "azurerm_role_assignment" "adf_key_vault_access" {
  scope                = var.key_vault_id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = azurerm_data_factory.main.identity[0].principal_id
}

resource "azurerm_data_factory_linked_service" "azure_databricks" {
  name            = "${var.prefix}-${var.environment}-ls-databricks-${var.suffix}"
  data_factory_id = azurerm_data_factory.main.id

  databricks_workspace {
    workspace_id = var.databricks_workspace_id
  }

  key_vault_password {
    linked_service_name = azurerm_data_factory_linked_service.key_vault.name
    secret_name         = "databricks-access-token"
  }
}

resource "azurerm_data_factory_linked_service" "azure_storage" {
  name            = "${var.prefix}-${var.environment}-ls-storage-${var.suffix}"
  data_factory_id = azurerm_data_factory.main.id

  connection_string = "DefaultEndpointsProtocol=https;AccountName=${var.storage_account_id};EndpointSuffix=core.windows.net"
}

resource "azurerm_data_factory_linked_service" "key_vault" {
  name            = "${var.prefix}-${var.environment}-ls-keyvault-${var.suffix}"
  data_factory_id = azurerm_data_factory.main.id

  key_vault {
    linked_service_name = azurerm_data_factory.main.name
    secret_name          = "storage-connection-string"
  }
}

output "id" {
  description = "Data Factory ID"
  value       = azurerm_data_factory.main.id
}

output "name" {
  description = "Data Factory name"
  value       = azurerm_data_factory.main.name
}
