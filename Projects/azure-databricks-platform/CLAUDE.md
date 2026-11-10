# Azure Data Platform Project

## Project objective

Build and maintain an enterprise Azure Data Platform using:

- Azure Databricks
- Azure Data Lake Storage Gen2
- Unity Catalog
- Delta Lake
- Azure Data Factory
- Azure Key Vault
- Microsoft Purview
- Azure DevOps
- Terraform
- Declarative Automation Bundles

## Architecture

Follow a Lakehouse architecture with the following layers:

- Bronze: raw, immutable ingestion
- Silver: validated, standardized and deduplicated data
- Gold: business-ready datasets and aggregates

Use Delta Lake tables and Unity Catalog for governance.

## Engineering standards

- Use Python 3.11 or the version supported by the target Databricks runtime.
- Use PySpark for distributed transformations.
- Keep business logic outside notebooks whenever possible.
- Notebooks should orchestrate reusable Python modules.
- Use type hints in Python code.
- Write unit tests for transformation logic.
- Use pytest for tests.
- Use Ruff for linting and formatting.
- Never hardcode credentials, tokens, workspace URLs or resource IDs.
- Never store secrets in source control.
- Use Microsoft Entra ID, managed identities or service principals.
- Use Key Vault or Databricks secret management where necessary.
- Use environment-specific configuration.
- Apply least-privilege access.

## Databricks standards

- Use Unity Catalog three-level namespace:
  catalog.schema.object
- Avoid DBFS mounts for new implementations.
- Prefer Unity Catalog external locations and storage credentials.
- Use Delta tables.
- Make pipelines idempotent.
- Add audit columns:
  - ingestion_timestamp
  - source_system
  - pipeline_run_id
- Use explicit schemas instead of relying on inference in production.
- Do not use collect() on large datasets.
- Avoid Python UDFs when Spark SQL functions are available.
- Configure jobs through Declarative Automation Bundles.
- Separate dev, test and prod targets.

## Infrastructure

Use Terraform for:

- Resource groups
- Networking
- ADLS accounts and containers
- Azure Databricks workspace
- Access Connector
- Key Vault
- Private Endpoints
- Azure Data Factory
- Log Analytics
- Microsoft Purview integration where applicable

Do not use Terraform to deploy application notebooks or Databricks jobs.
Use Declarative Automation Bundles for Databricks application resources.

## CI/CD

Every change must pass:

1. Formatting
2. Linting
3. Unit tests
4. Bundle validation
5. Terraform validation, when infrastructure changes
6. Security and secret scanning

Production deployment must require approval.

## Working instructions for Claude

Before changing code:

1. Read this CLAUDE.md.
2. Inspect existing conventions.
3. Explain any architectural assumption.
4. Prefer small and reviewable changes.
5. Do not create credentials or secret values.
6. Do not execute destructive Azure or Databricks commands.
7. Do not run terraform apply without explicit authorization.
8. Do not deploy to production without explicit authorization.

When generating code:

- Include error handling and logging.
- Include tests.
- Update documentation when behavior changes.
- Show the files that were created or modified.
- Highlight security implications.
