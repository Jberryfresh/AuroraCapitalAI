"""Base agent classes and utilities."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.start_time = datetime.utcnow()

    @abstractmethod
    async def initialize(self) -> None:
        """Set up any necessary resources or connections."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Clean up resources and connections."""
        pass

    @abstractmethod
    async def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's main task."""
        pass

    def log_activity(self, message: str, level: str = "INFO") -> None:
        """Log agent activity with timestamp."""
        timestamp = datetime.utcnow().isoformat()
        print(f"[{timestamp}] {level} - {self.name}: {message}")

    def get_runtime(self) -> float:
        """Get agent's runtime in seconds."""
        return (datetime.utcnow() - self.start_time).total_seconds()

class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass

class DataFetchError(AgentError):
    """Raised when an agent fails to fetch data."""
    pass

class DataValidationError(AgentError):
    """Raised when data fails validation."""
    pass
