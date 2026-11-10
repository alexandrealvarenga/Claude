"""Tool-related Pydantic models."""

from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Definition of a tool available to agents."""

    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema for parameters"
    )
    timeout_seconds: int = Field(
        default=30, ge=1, description="Tool execution timeout"
    )
    requires_approval: bool = Field(
        default=False, description="Requires human approval before execution"
    )


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution."""

    tool_name: str = Field(description="Name of the tool to execute")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters"
    )
    dry_run: bool = Field(default=False, description="Validate without executing")


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution."""

    success: bool = Field(description="Whether execution succeeded")
    output: Any = Field(default=None, description="Tool output")
    error: str | None = Field(default=None, description="Error message if failed")
    execution_time_ms: int = Field(description="Execution time in milliseconds")


class ToolListResponse(BaseModel):
    """Response model listing available tools."""

    tools: list[ToolDefinition] = Field(description="List of available tools")
