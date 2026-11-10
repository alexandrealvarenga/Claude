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

resource "azurerm_virtual_network" "main" {
  name                = "${var.prefix}-${var.environment}-vnet-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  address_space       = ["10.0.0.0/16"]
  tags                 = var.tags

  subnet {
    name           = "default"
    address_prefix = "10.0.0.0/24"
  }

  subnet {
    name           = "databricks"
    address_prefix = "10.0.1.0/24"
  }

  subnet {
    name           = "private-endpoints"
    address_prefix = "10.0.2.0/24"
  }
}

resource "azurerm_subnet" "databricks" {
  name                 = "databricks"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]

  delegation {
    name = "databricks-delegation"
    service_delegation {
      name    = "Microsoft.Databricks/workspaces"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
        "Microsoft.Network/virtualNetworks/subnets/prepareNetworkPolicies/action",
        "Microsoft.Network/virtualNetworks/subnets/action",
      ]
    }
  }
}

resource "azurerm_subnet" "private_endpoints" {
  name                 = "private-endpoints"
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.2.0/24"]

  private_endpoint_network_policies_enabled = true
}

resource "azurerm_network_security_group" "databricks" {
  name                = "${var.prefix}-${var.environment}-nsg-databricks-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags
}

resource "azurerm_route_table" "databricks" {
  name                = "${var.prefix}-${var.environment}-rt-databricks-${var.suffix}"
  location            = var.location
  resource_group_name = var.resource_group_name
  tags                = var.tags

  route {
    name                   = "default"
    address_prefix         = "0.0.0.0/0"
    next_hop_type          = "Internet"
  }
}

resource "azurerm_subnet_network_security_group_association" "databricks" {
  subnet_id                 = azurerm_subnet.databricks.id
  network_security_group_id = azurerm_network_security_group.databricks.id
}

resource "azurerm_subnet_route_table_association" "databricks" {
  subnet_id      = azurerm_subnet.databricks.id
  route_table_id = azurerm_route_table.databricks.id
}

output "vnet_id" {
  description = "Virtual Network ID"
  value       = azurerm_virtual_network.main.id
}

output "vnet_name" {
  description = "Virtual Network name"
  value       = azurerm_virtual_network.main.name
}

output "databricks_subnet_id" {
  description = "Databricks subnet ID"
  value       = azurerm_subnet.databricks.id
}

output "private_endpoints_subnet_id" {
  description = "Private endpoints subnet ID"
  value       = azurerm_subnet.private_endpoints.id
}
