"""
Base tool interface for all agent tools.
Provides a consistent interface and error handling framework.
"""
import asyncio
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

from utils.logger import logger


class ToolResult(BaseModel):
    """Standardized tool execution result."""
    success: bool = Field(..., description="Whether the tool execution succeeded")
    result: Any = Field(None, description="Tool execution result data")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ToolError(Exception):
    """Base exception for tool-related errors."""
    
    def __init__(self, message: str, tool_name: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(message)


class ToolConfig(BaseModel):
    """Configuration for tool behavior."""
    enabled: bool = Field(True, description="Whether the tool is enabled")
    max_execution_time: float = Field(30.0, description="Maximum execution time in seconds")
    retry_attempts: int = Field(0, description="Number of retry attempts on failure")
    safe_mode: bool = Field(True, description="Whether to run in safe mode with restrictions")
    allowed_paths: Optional[List[str]] = Field(None, description="Allowed file system paths")
    blocked_patterns: List[str] = Field(default_factory=list, description="Blocked file patterns")


class BaseTool(ABC):
    """
    Abstract base class for all agent tools.
    
    Provides a consistent interface for tool execution, error handling,
    security checks, and performance monitoring.
    """
    
    def __init__(self, config: Optional[ToolConfig] = None):
        self.config = config or ToolConfig()
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        
        logger.info(f"Initialized tool: {self.name}")
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for identification."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for agent understanding."""
        pass
    
    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """JSON schema for tool parameters."""
        pass
    
    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """
        Internal execution method to be implemented by subclasses.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ToolError: On execution failure
        """
        pass
    
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with error handling and monitoring.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            ToolResult with execution details
        """
        if not self.config.enabled:
            return ToolResult(
                success=False,
                error=f"Tool {self.name} is disabled",
                execution_time=0.0
            )
        
        start_time = time.time()
        self.execution_count += 1
        self.last_execution = datetime.now()
        
        logger.info(f"Executing tool: {self.name}", parameters=kwargs)
        
        try:
            # Validate parameters
            self._validate_parameters(kwargs)
            
            # Security checks
            self._security_check(kwargs)
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute(**kwargs),
                timeout=self.config.max_execution_time
            )
            
            execution_time = time.time() - start_time
            self.success_count += 1
            self.total_execution_time += execution_time
            
            logger.info(
                f"Tool execution successful: {self.name}",
                execution_time=f"{execution_time:.3f}s"
            )
            
            return ToolResult(
                success=True,
                result=result,
                execution_time=execution_time,
                metadata={
                    "tool_name": self.name,
                    "parameters": kwargs,
                    "timestamp": self.last_execution.isoformat()
                }
            )
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            self.error_count += 1
            error_msg = f"Tool execution timed out after {self.config.max_execution_time}s"
            
            logger.error(f"Tool timeout: {self.name}", execution_time=execution_time)
            
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=execution_time
            )
            
        except ToolError as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            
            logger.error(
                f"Tool error: {self.name}",
                error=e.message,
                details=e.details,
                execution_time=execution_time
            )
            
            return ToolResult(
                success=False,
                error=e.message,
                execution_time=execution_time,
                metadata={"error_details": e.details}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.error_count += 1
            
            logger.error(
                f"Unexpected tool error: {self.name}",
                error=str(e),
                execution_time=execution_time,
                exc_info=True
            )
            
            return ToolResult(
                success=False,
                error=f"Unexpected error: {str(e)}",
                execution_time=execution_time
            )
    
    def _validate_parameters(self, kwargs: Dict[str, Any]) -> None:
        """
        Validate tool parameters against schema.
        
        Args:
            kwargs: Parameters to validate
            
        Raises:
            ToolError: If validation fails
        """
        # TODO: Implement JSON schema validation
        pass
    
    def _security_check(self, kwargs: Dict[str, Any]) -> None:
        """
        Perform security checks on parameters.
        
        Args:
            kwargs: Parameters to check
            
        Raises:
            ToolError: If security check fails
        """
        if not self.config.safe_mode:
            return
        
        # Basic security checks can be implemented here
        # Subclasses should override for specific security needs
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tool execution statistics."""
        avg_execution_time = (
            self.total_execution_time / self.execution_count 
            if self.execution_count > 0 else 0
        )
        
        success_rate = (
            (self.success_count / self.execution_count) * 100
            if self.execution_count > 0 else 0
        )
        
        return {
            "tool_name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": success_rate,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_execution_time,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "enabled": self.config.enabled
        }
    
    def reset_statistics(self) -> None:
        """Reset tool execution statistics."""
        self.execution_count = 0
        self.success_count = 0
        self.error_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        
        logger.info(f"Reset statistics for tool: {self.name}")
    
    def to_function_spec(self) -> Dict[str, Any]:
        """
        Convert tool to OpenAI function specification.
        
        Returns:
            Function specification for OpenAI Function Calling
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema
        }
