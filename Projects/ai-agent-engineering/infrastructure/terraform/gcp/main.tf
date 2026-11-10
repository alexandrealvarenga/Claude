# =============================================================================
# Google Cloud Platform (GCP) - Terraform Configuration
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.20"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.20"
    }
  }

  backend "gcs" {
    bucket = "ai-agent-engineering-tfstate"
    prefix = "terraform/state"
  }
}

# =============================================================================
# Provider Configuration
# =============================================================================

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

provider "google-beta" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}

# =============================================================================
# Variables
# =============================================================================

variable "gcp_project_id" {
  description = "GCP project ID"
  type        = string
}

variable "gcp_region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "GCP zone"
  type        = string
  default     = "us-central1-a"
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

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

# =============================================================================
# Resources
# =============================================================================

resource "google_compute_network" "main" {
  name                    = "${var.app_name}-vpc-${var.environment}"
  auto_create_subnetworks = false
  description             = "VPC network for AI Agent Engineering"
}

resource "google_compute_subnetwork" "main" {
  name          = "${var.app_name}-subnet-${var.environment}"
  network       = google_compute_network.main.name
  ip_cidr_range = var.vpc_cidr
  region        = var.gcp_region

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_10_MIN"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# =============================================================================
# Outputs
# =============================================================================

output "project_id" {
  description = "GCP project ID"
  value       = var.gcp_project_id
}

output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "subnetwork_name" {
  description = "Subnetwork name"
  value       = google_compute_subnetwork.main.name
}

output "region" {
  description = "GCP region"
  value       = var.gcp_region
}
