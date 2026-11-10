"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models.agents import AgentConfig, AgentRequest, AgentStatus
from app.models.tools import ToolExecutionRequest


class TestAgentModels:
    """Test suite for agent models."""

    def test_agent_config_defaults(self) -> None:
        """Test AgentConfig default values."""
        config = AgentConfig()
        assert config.model == "gpt-4o"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.max_steps == 50
        assert config.timeout_seconds == 300
        assert config.human_in_the_loop is False

    def test_agent_config_custom_values(self) -> None:
        """Test AgentConfig with custom values."""
        config = AgentConfig(
            model="gpt-4o-mini",
            temperature=0.5,
            max_steps=25,
        )
        assert config.model == "gpt-4o-mini"
        assert config.temperature == 0.5
        assert config.max_steps == 25

    def test_agent_config_temperature_bounds(self) -> None:
        """Test AgentConfig temperature validation."""
        with pytest.raises(ValidationError):
            AgentConfig(temperature=2.5)  # Above max

        with pytest.raises(ValidationError):
            AgentConfig(temperature=-0.1)  # Below min

    def test_agent_request_valid(self) -> None:
        """Test valid AgentRequest creation."""
        request = AgentRequest(
            task="Search for AI agents",
            instructions="Use the search tool",
        )
        assert request.task == "Search for AI agents"
        assert request.instructions == "Use the search tool"
        assert request.config is None

    def test_agent_request_with_config(self) -> None:
        """Test AgentRequest with agent config."""
        config = AgentConfig(model="gpt-4o-mini", temperature=0.3)
        request = AgentRequest(
            task="Test task",
            config=config,
            context={"user_id": "123"},
        )
        assert request.config.model == "gpt-4o-mini"
        assert request.context["user_id"] == "123"

    def test_agent_status_enum(self) -> None:
        """Test AgentStatus enum values."""
        assert AgentStatus.PENDING.value == "pending"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.COMPLETED.value == "completed"
        assert AgentStatus.FAILED.value == "failed"


class TestToolModels:
    """Test suite for tool models."""

    def test_tool_execution_request_valid(self) -> None:
        """Test valid ToolExecutionRequest creation."""
        request = ToolExecutionRequest(
            tool_name="web_search",
            parameters={"query": "AI agents"},
        )
        assert request.tool_name == "web_search"
        assert request.parameters["query"] == "AI agents"
        assert request.dry_run is False

    def test_tool_execution_request_dry_run(self) -> None:
        """Test ToolExecutionRequest dry run mode."""
        request = ToolExecutionRequest(
            tool_name="web_search",
            parameters={"query": "test"},
            dry_run=True,
        )
        assert request.dry_run is True
