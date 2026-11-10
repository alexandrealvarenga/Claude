"""Agent-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent execution status."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentConfig(BaseModel):
    """Configuration for agent execution."""

    model: str = Field(default="gpt-4o", description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1)
    max_steps: int = Field(default=50, ge=1, description="Maximum agent steps")
    timeout_seconds: int = Field(
        default=300, ge=1, description="Agent timeout in seconds"
    )
    human_in_the_loop: bool = Field(
        default=False, description="Require human approval for actions"
    )


class AgentStep(BaseModel):
    """Represents a single step in agent execution."""

    step_number: int = Field(description="Step number")
    action: str = Field(description="Action taken in this step")
    reasoning: str | None = Field(default=None, description="LLM reasoning")
    tool_calls: list[dict[str, Any]] = Field(
        default_factory=list, description="Tools called in this step"
    )
    result: Any = Field(default=None, description="Step result")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentRequest(BaseModel):
    """Request model for agent execution."""

    task: str = Field(description="Task description for the agent")
    instructions: str | None = Field(
        default=None, description="Additional instructions"
    )
    config: AgentConfig | None = Field(default=None, description="Agent configuration")
    context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task": "Search for information about AI agents",
                    "instructions": "Use the web search tool to find relevant information",
                    "config": {"model": "gpt-4o", "temperature": 0.7},
                }
            ]
        }
    }


class AgentResponse(BaseModel):
    """Response model for agent execution."""

    task_id: str = Field(description="Unique task identifier")
    status: AgentStatus = Field(description="Current task status")
    result: Any = Field(default=None, description="Agent result")
    steps: list[AgentStep] = Field(
        default_factory=list, description="Execution steps taken"
    )
    error: str | None = Field(default=None, description="Error message if failed")


class AgentStatusResponse(BaseModel):
    """Response model for agent status queries."""

    task_id: str = Field(description="Unique task identifier")
    status: AgentStatus = Field(description="Current task status")
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    current_step: int = Field(default=0, description="Current step number")
    total_steps: int = Field(default=0, description="Total expected steps")
    started_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)
