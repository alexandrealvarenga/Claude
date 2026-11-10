terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100.0"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.35.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  skip_provider_registration = true
}

provider "databricks" {
  host = module.databricks.workspace_url
}

variable "environment" {
  description = "Deployment environment (dev, test, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be dev, test, or prod."
  }
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "resource_prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "dataplatform"
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    environment = "dev"
    project     = "data-platform"
    managed_by = "terraform"
  }
}

locals {
  common_tags = merge(var.tags, {
    environment = var.environment
  })

  resource_suffix = random_string.suffix.result
}

resource "random_string" "suffix" {
  length  = 5
  special = false
  upper   = false
  numeric = true
}

module "resource_group" {
  source = "./modules/resource-group"

  environment = var.environment
  location    = var.location
  prefix      = var.resource_prefix
  suffix      = local.resource_suffix
  tags        = local.common_tags
}

module "networking" {
  source = "./modules/networking"

  environment        = var.environment
  location           = var.location
  resource_group_name = module.resource_group.name
  prefix             = var.resource_prefix
  suffix             = local.resource_suffix
  tags               = local.common_tags

  depends_on = [module.resource_group]
}

module "storage" {
  source = "./modules/storage"

  environment        = var.environment
  location           = var.location
  resource_group_name = module.resource_group.name
  prefix             = var.resource_prefix
  suffix             = local.resource_suffix
  tags               = local.common_tags

  depends_on = [module.resource_group]
}

module "key_vault" {
  source = "./modules/key-vault"

  environment        = var.environment
  location           = var.location
  resource_group_name = module.resource_group.name
  prefix             = var.resource_prefix
  suffix             = local.resource_suffix
  tags               = local.common_tags

  storage_account_id = module.storage.account_id

  depends_on = [module.storage]
}

module "databricks" {
  source = "./modules/databricks-workspace"

  environment        = var.environment
  location           = var.location
  resource_group_name = module.resource_group.name
  prefix             = var.resource_prefix
  suffix             = local.resource_suffix
  tags               = local.common_tags

  subnet_id           = module.networking.databricks_subnet_id
  vnet_id             = module.networking.vnet_id
  key_vault_id        = module.key_vault.id

  depends_on = [module.networking, module.key_vault]
}

module "data_factory" {
  source = "./modules/data-factory"

  environment        = var.environment
  location           = var.location
  resource_group_name = module.resource_group.name
  prefix             = var.resource_prefix
  suffix             = local.resource_suffix
  tags               = local.common_tags

  databricks_workspace_id = module.databricks.workspace_id
  storage_account_id      = module.storage.account_id
  key_vault_id            = module.key_vault.id

  depends_on = [module.databricks, module.storage, module.key_vault]
}

module "log_analytics" {
  source = "./modules/log-analytics"

  environment        = var.environment
  location           = var.location
  resource_group_name = module.resource_group.name
  prefix             = var.resource_prefix
  suffix             = local.resource_suffix
  tags               = local.common_tags

  depends_on = [module.resource_group]
}

output "resource_group_name" {
  description = "Name of the resource group"
  value       = module.resource_group.name
}

output "storage_account_name" {
  description = "Name of the storage account"
  value       = module.storage.account_name
}

output "databricks_workspace_url" {
  description = "Databricks workspace URL"
  value       = module.databricks.workspace_url
}

output "key_vault_url" {
  description = "Key Vault URL"
  value       = module.key_vault.vault_url
}

output "data_factory_name" {
  description = "Data Factory name"
  value       = module.data_factory.name
}
