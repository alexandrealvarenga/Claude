"""Unit tests for health endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestHealthEndpoints:
    """Test suite for health check endpoints."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        return TestClient(app)

    def test_health_check(self, client: TestClient) -> None:
        """Test the health check endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_readiness_check(self, client: TestClient) -> None:
        """Test the readiness check endpoint returns ready status."""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}
