# =============================================================================
# Azure Infrastructure - Terraform Configuration
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 1.13"
    }
  }

  backend "azurerm" {
    container_name = "tfstate"
    key            = "ai-agent-engineering/terraform.tfstate"
  }
}

# =============================================================================
# Provider Configuration
# =============================================================================

provider "azurerm" {
  features {}

  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
  client_id       = var.azure_client_id
  client_secret   = var.azure_client_secret
}

# =============================================================================
# Variables
# =============================================================================

variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
  sensitive   = true
}

variable "azure_tenant_id" {
  description = "Azure tenant ID"
  type        = string
  sensitive   = true
}

variable "azure_client_id" {
  description = "Azure client ID (service principal)"
  type        = string
  sensitive   = true
}

variable "azure_client_secret" {
  description = "Azure client secret"
  type        = string
  sensitive   = true
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "ai-agent"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-ai-agent-engineering"
}

# =============================================================================
# Resources
# =============================================================================

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    environment = var.environment
    application = var.app_name
    managed_by  = "terraform"
  }
}

# =============================================================================
# Outputs
# =============================================================================

output "resource_group_name" {
  description = "Resource group name"
  value       = azurerm_resource_group.main.name
}

output "resource_group_id" {
  description = "Resource group ID"
  value       = azurerm_resource_group.main.id
}

output "location" {
  description = "Azure region"
  value       = azurerm_resource_group.main.location
}
