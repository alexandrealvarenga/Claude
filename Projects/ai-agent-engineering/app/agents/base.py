"""Base agent implementation using LangGraph."""

from abc import ABC, abstractmethod
from typing import Any, TypedDict

from langgraph.graph import StateGraph


class AgentState(TypedDict):
    """Base state for all agents."""

    task: str
    context: dict[str, Any]
    result: Any | None
    steps: list[dict[str, Any]]
    error: str | None


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str, description: str):
        """Initialize the base agent.

        Args:
            name: Agent name.
            description: Agent description.
        """
        self.name = name
        self.description = description
        self.graph: StateGraph | None = None

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Build the agent's state graph.

        Returns:
            Compiled LangGraph state machine.
        """
        pass

    @abstractmethod
    async def execute(self, task: str, context: dict[str, Any] | None = None) -> Any:
        """Execute the agent task.

        Args:
            task: Task description.
            context: Optional execution context.

        Returns:
            Task result.
        """
        pass
