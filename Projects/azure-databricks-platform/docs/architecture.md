# Azure Data Platform Architecture

## Overview

This document describes the architecture of the Azure Data Platform built on Azure Databricks with a Lakehouse pattern.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Azure Cloud                                    │
│                                                                          │
│  ┌──────────────────┐     ┌─────────────────────────────────────────┐  │
│  │   Azure DevOps    │     │         Azure Virtual Network           │  │
│  │   CI/CD Pipeline  │     │  ┌─────────────────────────────────────┐ │  │
│  └────────┬─────────┘     │  │         Private Endpoints             │ │  │
│           │              │  └─────────────────────────────────────┘ │  │
│           │              │              │                              │  │
│           │              │  ┌────────────┴────────────┐                  │  │
│           │              │  │                         │                  │  │
│           │              │  ▼                         ▼                  │  │
│           │              │  ┌─────────────┐   ┌──────────────┐           │  │
│           │              │  │ Databricks  │   │ Data Factory │           │  │
│           │              │  │  Workspace  │   │              │           │  │
│           │              │  └─────────────┘   └──────────────┘           │  │
│           │              └───────────────────────────────────────────── │  │
│           │                         │                                      │
│           │                         ▼                                      │
│           │              ┌────────────────────────┐                       │
│           │              │    Unity Catalog       │                       │
│           │              │  ┌────┬────┬────┐     │                       │
│           │              │  │Dev │Test│Prod│     │                       │
│           │              │  └────┴────┴────┘     │                       │
│           │              └────────────────────────┘                       │
│           │                         │                                      │
│           │                         ▼                                      │
│           │              ┌─────────────────────────────┐                  │
│           │              │      ADLS Gen2               │                  │
│           │              │  ┌─────┬─────┬─────┐        │                  │
│           │              │  │Bronze│Silver│Gold │       │                  │
│           │              │  └─────┴─────┴─────┘        │                  │
│           │              └─────────────────────────────┘                  │
│           │                                                             │
│           │              ┌─────────────────────────────┐                  │
│           │              │       Azure Key Vault        │                  │
│           │              └─────────────────────────────┘                  │
│           │                                                             │
│           │              ┌─────────────────────────────┐                  │
│           │              │       Log Analytics         │                  │
│           └──────────────┴─────────────────────────────┴──────────────────┘
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

## Data Architecture

### Lakehouse Layers

#### Bronze Layer (Raw)
- **Purpose**: Immutable raw data ingestion
- **Format**: Delta Lake
- **Retention**: Long-term
- **Access**: Data engineers only
- **Characteristics**:
  - Raw, untransformed data from source systems
  - Schema-on-read
  - Full audit trail with `ingestion_timestamp`, `source_system`, `pipeline_run_id`
  - Immutable - data is never modified

#### Silver Layer (Cleansed)
- **Purpose**: Validated, standardized, deduplicated data
- **Format**: Delta Lake
- **Access**: Data engineers and analysts
- **Transformations**:
  - Schema enforcement
  - Data type standardization
  - Deduplication
  - Business rule application
  - Slowly Changing Dimensions (SCD) Type 2

#### Gold Layer (Business-Ready)
- **Purpose**: Curated datasets for analytics and reporting
- **Format**: Delta Lake
- **Access**: All users including BI tools
- **Contents**:
  - Aggregated metrics
  - Business-defined datasets
  - Pre-calculated KPIs
  - Machine learning feature stores

### Unity Catalog Namespace

```
catalog.schema.table
```

Example:
```
dev.bronze.raw_customers
dev.silver.curated_customers
dev.gold.customer_analytics
```

## Infrastructure Components

### Resource Groups
- Logical grouping of related resources
- One resource group per environment (dev, test, prod)
- Tag-based cost tracking

### Networking
- Virtual Network with private endpoints
- Dedicated subnets:
  - Databricks
  - Private endpoints
- Network Security Groups (NSG)
- Route tables for Databricks traffic

### Storage (ADLS Gen2)
- Hierarchical namespace enabled
- Containers: bronze, silver, gold, tmp
- Zone-redundant storage (ZRS)
- TLS 1.2 minimum
- Firewall rules blocking public access

### Azure Databricks
- Premium tier for Unity Catalog
- Serverless compute (no public IPs)
- Private connectivity via VNet injection
- Key Vault integration for secrets

### Azure Data Factory
- Orchestration layer
- Linked services for Databricks and Storage
- System-assigned managed identity
- Key Vault integration

### Azure Key Vault
- Secrets management
- RBAC authorization
- Soft delete enabled
- Purge protection in prod

### Log Analytics
- Centralized logging
- Container Insights
- Retention: 7 days (dev/test), 30 days (prod)

## Security Architecture

### Authentication
- **Microsoft Entra ID** for all user authentication
- **Managed Identity** for service-to-service
- **Service Principals** for CI/CD pipelines
- No personal access tokens in code

### Authorization
- Role-Based Access Control (RBAC)
- Unity Catalog for data access control
- Key Vault for secret access
-least privilege principle

### Network Security
- Private endpoints for all Azure services
- VNet integration for Databricks
- Firewall rules restricting access
- No public IP exposure

### Secrets Management
- All secrets in Azure Key Vault
- Service Principals for pipeline access
- Certificate-based authentication where possible

## CI/CD Pipeline

### Stages
1. **Lint and Format** - Ruff validation
2. **Unit Tests** - pytest with coverage
3. **Bundle Validation** - Databricks bundle syntax
4. **Terraform Validation** - plan and validate
5. **Security Scan** - secret detection
6. **Deploy Dev** - automatic on develop branch
7. **Deploy Test** - automatic after dev
8. **Approval** - manual for production
9. **Deploy Prod** - after approval

### Branch Strategy
- `main` - production code
- `develop` - integration branch
- Feature branches for changes

## Environments

| Environment | Purpose | Deployment | Approval |
|------------|---------|------------|----------|
| dev | Development testing | Automatic | None |
| test | Integration testing | Automatic | None |
| prod | Production | Manual | Required |

## Databricks Automation Bundles

Bundles define jobs and pipelines as code:

```yaml
bundle:
  name: dataplatform-dev
  target: dev

resources:
  jobs:
    bronze_ingestion_job:
      notebook_task:
        notebook_path: /Workspace/Platform/Bronze/Ingestion
  pipelines:
    bronze_to_silver_pipeline:
      target: silver
```

## Operational Considerations

### Monitoring
- Databricks monitoring dashboards
- ADF pipeline monitoring
- Log Analytics queries
- Alerting on failures

### Backup and Recovery
- ADLS soft delete enabled
- Delta Lake time travel
- Terraform state in secure backend

### Cost Management
- Serverless compute when possible
- Auto-scaling clusters
- Tag-based cost allocation
- Budget alerts

## Disaster Recovery

- Multi-region deployment for prod
- Geo-redundant storage option
- Backup and restore procedures documented separately
- RTO/RPO targets defined per environment

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Engineering standards
- [Terraform modules](../infrastructure/) - Infrastructure as code
- [Bundles](../bundles/) - Databricks automation
- [Source code](../src/platform/) - Data transformation logic
