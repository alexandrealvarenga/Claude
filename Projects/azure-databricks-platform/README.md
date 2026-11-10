# Azure Databricks Data Platform

Enterprise data platform built on Azure Databricks with Lakehouse architecture.

## Quick Links

- [Architecture Documentation](docs/architecture.md)
- [Engineering Standards](CLAUDE.md)

## Project Structure

```
azure-databricks-platform/
├── src/platform/           # Python/PySpark source code
│   ├── bronze/             # Raw ingestion layer
│   ├── silver/             # Cleansed layer
│   ├── gold/               # Business-ready layer
│   ├── config.py           # Configuration management
│   └── auth.py             # Azure authentication
├── tests/                  # Unit and integration tests
├── infrastructure/         # Terraform modules
│   ├── modules/            # Reusable Terraform modules
│   └── environments/       # Environment-specific tfvars
├── bundles/                # Databricks Automation Bundles
│   ├── dev/
│   ├── test/
│   └── prod/
├── pipelines/              # Azure DevOps CI/CD
└── docs/                   # Architecture documentation
```

## Getting Started

### Prerequisites

- Python 3.11+
- Azure subscription
- Azure DevOps project
- Terraform 1.7+

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Install Spark (for local testing)
pip install pyspark==3.5.0

# Run tests
pytest tests/unit/ -v

# Run linting
ruff check src/ tests/
```

### Environment Variables

```bash
# Azure Configuration
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_LOCATION="eastus"

# Storage Configuration
export STORAGE_ACCOUNT_NAME="your-storage-account"

# Databricks Configuration
export DATABRICKS_WORKSPACE_URL="https://adb-xxx.azuredatabricks.net"
export DATABRICKS_CATALOG="main"

# Key Vault
export KEY_VAULT_URL="https://your-keyvault.vault.azure.net/"

# Pipeline Configuration
export ENVIRONMENT="dev"
export PIPELINE_RUN_ID="run-$(uuidgen)"
export SOURCE_SYSTEM="local-development"
```

## Deployment

### Infrastructure (Terraform)

```bash
cd infrastructure

# Initialize
terraform init

# Plan
terraform plan -var-file=environments/dev.tfvars

# Apply (requires authorization)
terraform apply -var-file=environments/dev.tfvars
```

### Databricks Bundles

```bash
databricks bundle deploy dev
databricks bundle validate test
databricks bundle deploy prod
```

## Data Layers

### Bronze (Raw)
Immutable raw data from source systems. See [bronze module](src/platform/bronze/).

### Silver (Cleansed)
Validated, standardized, deduplicated data. See [silver module](src/platform/silver/).

### Gold (Business)
Aggregated, business-ready datasets. See [gold module](src/platform/gold/).

## Security

- No credentials in source code
- Secrets stored in Azure Key Vault
- Managed Identity for Azure resources
- RBAC for access control
- Private endpoints for network isolation

## Contributing

See [CLAUDE.md](CLAUDE.md) for engineering standards and contribution guidelines.

## License

MIT
