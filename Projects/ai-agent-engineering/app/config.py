"""Application Configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = Field(default="development", description="Application environment")
    app_host: str = Field(default="0.0.0.0", description="Application host")
    app_port: int = Field(default=8000, description="Application port")
    app_debug: bool = Field(default=False, description="Debug mode")

    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format (json or text)")

    # LLM Provider
    openai_api_key: str = Field(default="", description="OpenAI API key")
    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    llm_model: str = Field(default="gpt-4o", description="LLM model name")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=4096, ge=1)

    # Azure
    azure_subscription_id: str = Field(default="", description="Azure subscription ID")
    azure_tenant_id: str = Field(default="", description="Azure tenant ID")
    azure_client_id: str = Field(default="", description="Azure client ID")
    azure_client_secret: str = Field(default="", description="Azure client secret")
    azure_location: str = Field(default="eastus", description="Azure location")
    azure_openai_endpoint: str = Field(default="", description="Azure OpenAI endpoint")
    azure_openai_key: str = Field(default="", description="Azure OpenAI key")

    # AWS
    aws_region: str = Field(default="us-east-1", description="AWS region")
    aws_access_key_id: str = Field(default="", description="AWS access key ID")
    aws_secret_access_key: str = Field(default="", description="AWS secret access key")
    aws_session_token: str = Field(default="", description="AWS session token")
    aws_bedrock_endpoint: str = Field(default="", description="AWS Bedrock endpoint")

    # OCI
    oci_region: str = Field(default="us-ashburn-1", description="OCI region")
    oci_tenancy_id: str = Field(default="", description="OCI tenancy ID")
    oci_user_id: str = Field(default="", description="OCI user ID")
    oci_fingerprint: str = Field(default="", description="OCI key fingerprint")
    oci_key_file: str = Field(default="", description="OCI private key file path")
    oci_passphrase: str = Field(default="", description="OCI key passphrase")
    oci_compartment_id: str = Field(default="", description="OCI compartment ID")

    # GCP
    gcp_project_id: str = Field(default="", description="GCP project ID")
    gcp_region: str = Field(default="us-central1", description="GCP region")
    gcp_zone: str = Field(default="us-central1-a", description="GCP zone")
    google_application_credentials: str = Field(
        default="", description="GCP service account JSON"
    )

    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/ai_agents",
        description="Database connection URL",
    )
    database_pool_size: int = Field(default=10, ge=1)
    database_max_overflow: int = Field(default=20, ge=0)

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis URL")
    redis_password: str = Field(default="", description="Redis password")

    # MCP
    mcp_server_url: str = Field(
        default="http://localhost:3000", description="MCP server URL"
    )
    mcp_server_auth_token: str = Field(default="", description="MCP server auth token")

    # Observability
    otel_exporter_otlp_endpoint: str = Field(
        default="http://localhost:4317", description="OTLP exporter endpoint"
    )
    otel_service_name: str = Field(
        default="ai-agent-engineering", description="OpenTelemetry service name"
    )
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    tracing_enabled: bool = Field(default=True, description="Enable tracing")

    # Security
    secret_key: str = Field(
        default="change-this-in-production", description="Secret key for security"
    )
    allowed_hosts: str = Field(default="localhost,127.0.0.1", description="Allowed hosts")
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="CORS allowed origins",
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, ge=1)

    # Agent Configuration
    agent_max_steps: int = Field(default=50, ge=1, description="Max agent steps")
    agent_timeout_seconds: int = Field(
        default=300, ge=1, description="Agent timeout in seconds"
    )
    agent_human_in_the_loop: bool = Field(
        default=False, description="Enable human in the loop"
    )
    agent_tool_timeout_seconds: int = Field(
        default=30, ge=1, description="Tool execution timeout"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Dependency injection type
SettingsDep = Annotated[Settings, None]
