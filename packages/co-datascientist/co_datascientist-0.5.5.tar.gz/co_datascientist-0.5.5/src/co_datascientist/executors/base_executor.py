"""Base executor interface for code execution across different platforms."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models import CodeResult


class BaseExecutor(ABC):
    """Abstract base class for code executors.
    
    All executors must implement the execute method to run Python code
    and return standardized results.
    """
    
    def __init__(self, python_path: str = "python", config: Dict[str, Any] = None):
        """Initialize the executor.
        
        Args:
            python_path: Path to Python interpreter (may be ignored by cloud executors)
            config: Platform-specific configuration dictionary
        """
        self.python_path = python_path
        self.config = config or {}
    
    @abstractmethod
    def execute(self, code: str) -> CodeResult:
        """Execute Python code and return results.
        
        Args:
            code: Python code to execute
            
        Returns:
            CodeResult containing stdout, stderr, return_code, and runtime_ms
        """
        pass
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the name of this execution platform."""
        pass
    
    def is_available(self) -> bool:
        """Check if this executor is available/configured properly.
        
        Returns:
            True if the executor can be used, False otherwise
        """
        return True
