# =============================================================================
# Oracle Cloud Infrastructure (OCI) - Terraform Configuration
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 5.30"
    }
  }

  backend "http" {
    # OCI Object Storage backend configuration
    address = "https://objectstorage.us-ashburn-1.oraclecloud.com"
  }
}

# =============================================================================
# Provider Configuration
# =============================================================================

provider "oci" {
  region = var.oci_region

  config_file_profile = "DEFAULT"
}

# =============================================================================
# Variables
# =============================================================================

variable "oci_region" {
  description = "OCI region"
  type        = string
  default     = "us-ashburn-1"
}

variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
  sensitive   = true
}

variable "compartment_ocid" {
  description = "OCI compartment OCID"
  type        = string
  sensitive   = true
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

# =============================================================================
# Resources
# =============================================================================

resource "oci_identity_compartment" "main" {
  count      = var.compartment_ocid == "" ? 1 : 0
  name       = "${var.app_name}-compartment-${var.environment}"
  description = "Compartment for AI Agent Engineering resources"
  parent_ocid = var.tenancy_ocid
}

data "oci_identity_compartment" "main" {
  count   = var.compartment_ocid != "" ? 1 : 0
  id      = var.compartment_ocid
}

locals {
  compartment_id = var.compartment_ocid != "" ? data.oci_identity_compartment.main[0].id : oci_identity_compartment.main[0].id
}

resource "oci_core_vcn" "main" {
  compartment_id = local.compartment_id
  display_name   = "${var.app_name}-vcn-${var.environment}"
  cidr_blocks    = ["10.0.0.0/16"]
}

# =============================================================================
# Outputs
# =============================================================================

output "vcn_id" {
  description = "VCN ID"
  value       = oci_core_vcn.main.id
}

output "vcn_cidr" {
  description = "VCN CIDR block"
  value       = oci_core_vcn.main.cidr_blocks[0]
}

output "compartment_id" {
  description = "Compartment OCID"
  value       = local.compartment_id
}

output "region" {
  description = "OCI region"
  value       = var.oci_region
}
