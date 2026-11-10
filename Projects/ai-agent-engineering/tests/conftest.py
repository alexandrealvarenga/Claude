"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_settings(mocker):
    """Mock application settings for testing."""
    settings = mocker.MagicMock()
    settings.app_env = "test"
    settings.app_debug = False
    settings.log_level = "DEBUG"
    settings.log_format = "text"
    settings.cors_origins = ["http://localhost:3000"]
    settings.secret_key = "test-secret-key"
    settings.rate_limit_enabled = False
    settings.otel_service_name = "ai-agent-test"
    settings.metrics_enabled = False
    settings.tracing_enabled = False
    settings.database_url = "postgresql://test:test@localhost:5432/test"
    settings.redis_url = "redis://localhost:6379/0"
    return settings
