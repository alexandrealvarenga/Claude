variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "location" {
  description = "Azure region"
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
  description = "Tags to apply to the resource group"
  type        = map(string)
}

resource "azurerm_resource_group" "main" {
  name     = "${var.prefix}-${var.environment}-rg-${var.suffix}"
  location = var.location
  tags     = var.tags
}

output "name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "id" {
  description = "Resource group ID"
  value       = azurerm_resource_group.main.id
}

output "location" {
  description = "Resource group location"
  value       = azurerm_resource_group.main.location
}
