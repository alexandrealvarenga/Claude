"""Agents API Endpoints."""

from fastapi import APIRouter, HTTPException

from app.models.agents import AgentRequest, AgentResponse, AgentStatusResponse
from app.observability.logging import get_logger

router = APIRouter()
log = get_logger(__name__)


@router.post("/agents/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest) -> AgentResponse:
    """Run an agent task.

    Args:
        request: Agent execution request with task and configuration.

    Returns:
        Agent execution response with results.

    Raises:
        HTTPException: If agent execution fails.
    """
    log.info(
        "agent_run_started",
        task=request.task,
        model=request.config.model if request.config else None,
    )

    try:
        # Placeholder - actual implementation would use LangGraph
        result = {
            "task_id": "placeholder-task-id",
            "status": "completed",
            "result": {"message": "Agent execution placeholder"},
            "steps": [],
        }

        return AgentResponse(
            task_id=result["task_id"],
            status=result["status"],
            result=result["result"],
            steps=result["steps"],
        )

    except Exception as e:
        log.error("agent_run_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e}")


@router.get("/agents/{task_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(task_id: str) -> AgentStatusResponse:
    """Get status of an agent task.

    Args:
        task_id: Unique identifier of the agent task.

    Returns:
        Agent status response.

    Raises:
        HTTPException: If task not found.
    """
    log.info("agent_status_check", task_id=task_id)

    # Placeholder - actual implementation would check stored state
    return AgentStatusResponse(
        task_id=task_id,
        status="completed",
        progress=100,
        current_step=10,
        total_steps=10,
    )
