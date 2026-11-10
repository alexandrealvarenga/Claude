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

resource "azurerm_log_analytics_workspace" "main" {
  name                = "${var.prefix}-${var.environment}-log-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  sku                 = var.environment == "prod" ? "PerGB2018" : "Free"
  retention_in_days   = var.environment == "prod" ? 30 : 7
  tags                = var.tags
}

resource "azurerm_log_analytics_solution" "main" {
  solution_name         = "ContainerInsights"
  workspace_name        = azurerm_log_analytics_workspace.main.name
  workspace_resource_id = azurerm_log_analytics_workspace.main.id
  plan {
    publisher = "Microsoft"
    product   = "OMContainerInsights"
  }
}

output "workspace_id" {
  description = "Log Analytics workspace ID"
  value       = azurerm_log_analytics_workspace.main.id
}

output "workspace_name" {
  description = "Log Analytics workspace name"
  value       = azurerm_log_analytics_workspace.main.name
}

output "workspace_customer_id" {
  description = "Log Analytics customer ID"
  value       = azurerm_log_analytics_workspace.main.customer_id
}
