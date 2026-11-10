# AI Agent Engineering

Engineering of AI Agents, Automation and Multicloud Development.

## Overview

This project provides a modular framework for building, deploying and orchestrating AI agents in enterprise environments across multiple cloud providers.

## Features

- **Agent Framework**: Built on LangGraph for complex agent workflows
- **Multi-Cloud Support**: Azure, AWS, Oracle Cloud Infrastructure, and Google Cloud
- **FastAPI Backend**: RESTful API for agent interaction
- **MCP Integration**: Model Context Protocol for extensible tool integrations
- **Infrastructure as Code**: Terraform modules for all supported clouds
- **Observability**: Structured logging, metrics and tracing

## Tech Stack

- Python 3.11+
- FastAPI
- Pydantic v2
- LangGraph
- Docker
- Terraform
- Pytest

## Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Terraform 1.5+

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-agent-engineering

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"

# Copy environment variables
cp .env.example .env
```

### Configuration

Edit `.env` with your cloud credentials and settings:

```bash
# Application
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO

# Cloud Provider (select one or more)
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id

AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

OCI_REGION=us-ashburn-1
OCI_TENANCY_ID=your-tenancy-id
OCI_USER_ID=your-user-id

GCP_PROJECT_ID=your-project-id
GCP_REGION=us-central1

# LLM Provider
OPENAI_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4o
```

### Running Locally

```bash
# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running with Docker

```bash
# Build and start containers
docker-compose up --build

# Run in background
docker-compose up --build -d
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Project Structure

```
ai-agent-engineering/
├── app/                    # Application code
│   ├── agents/           # Agent implementations
│   ├── workflows/         # Workflow definitions
│   ├── tools/             # Agent tools
│   ├── integrations/      # External integrations
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   ├── security/          # Security utilities
│   ├── observability/     # Logging, metrics, tracing
│   └── config/            # Configuration management
├── infrastructure/        # IaC modules
│   ├── terraform/         # Terraform configurations
│   │   ├── azure/
│   │   ├── aws/
│   │   ├── oci/
│   │   └── gcp/
│   └── kubernetes/       # K8s manifests
├── tests/                  # Test suites
│   ├── unit/
│   └── integration/
└── docs/                  # Documentation
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/agents/run` | Run an agent task |
| GET | `/api/v1/agents/{id}/status` | Get agent task status |
| POST | `/api/v1/tools/execute` | Execute a tool |
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |

## Documentation

For full documentation, see the `/docs` directory.

## License

MIT
