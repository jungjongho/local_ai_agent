"""
Models for system-related operations (Phase 3).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SystemCommand(BaseModel):
    """System command execution request."""
    command: str = Field(..., description="Command to execute")
    working_directory: Optional[str] = Field(None, description="Working directory")
    timeout: int = Field(default=30, ge=1, le=300, description="Timeout in seconds")
    safe_mode: bool = Field(default=True, description="Use safe command whitelist")


class CommandResult(BaseModel):
    """System command execution result."""
    success: bool = Field(..., description="Whether command succeeded")
    return_code: int = Field(..., description="Command return code")
    stdout: str = Field(..., description="Standard output")
    stderr: str = Field(..., description="Standard error")
    execution_time: float = Field(..., description="Execution time in seconds")


class FileOperation(BaseModel):
    """File system operation request."""
    operation: str = Field(..., description="Operation type (read, write, delete, etc.)")
    path: str = Field(..., description="File or directory path")
    content: Optional[str] = Field(None, description="Content for write operations")
    destination: Optional[str] = Field(None, description="Destination for move/copy")
    recursive: bool = Field(default=False, description="Recursive operation for directories")


class FileOperationResult(BaseModel):
    """File operation result."""
    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Result message")
    path: str = Field(..., description="Operated path")
    size: Optional[int] = Field(None, description="File size in bytes")
    modified_time: Optional[datetime] = Field(None, description="Last modified time")


class DirectoryWatcher(BaseModel):
    """Directory watcher configuration."""
    path: str = Field(..., description="Directory path to watch")
    recursive: bool = Field(default=True, description="Watch subdirectories")
    file_patterns: List[str] = Field(default_factory=list, description="File patterns to watch")
    ignore_patterns: List[str] = Field(default_factory=list, description="Patterns to ignore")


class WatcherEvent(BaseModel):
    """File system event from watcher."""
    event_type: str = Field(..., description="Event type (created, modified, deleted, moved)")
    path: str = Field(..., description="File path")
    timestamp: datetime = Field(..., description="Event timestamp")
    is_directory: bool = Field(..., description="Whether path is directory")


class ApplicationLaunch(BaseModel):
    """Application launch request."""
    application: str = Field(..., description="Application name or path")
    arguments: List[str] = Field(default_factory=list, description="Command line arguments")
    working_directory: Optional[str] = Field(None, description="Working directory")
    environment: Optional[Dict[str, str]] = Field(None, description="Environment variables")


class TaskSchedule(BaseModel):
    """Task scheduling request."""
    task_id: str = Field(..., description="Unique task identifier")
    schedule_type: str = Field(..., description="Schedule type (interval, cron, once)")
    schedule_value: str = Field(..., description="Schedule specification")
    task_data: Dict[str, Any] = Field(..., description="Task execution data")
    enabled: bool = Field(default=True, description="Whether task is enabled")


class ScheduledTask(BaseModel):
    """Scheduled task information."""
    task_id: str = Field(..., description="Task identifier")
    schedule_type: str = Field(..., description="Schedule type")
    schedule_value: str = Field(..., description="Schedule specification")
    next_run: Optional[datetime] = Field(None, description="Next execution time")
    last_run: Optional[datetime] = Field(None, description="Last execution time")
    enabled: bool = Field(..., description="Whether task is enabled")
    run_count: int = Field(default=0, description="Number of times executed")


class SystemInfo(BaseModel):
    """System information."""
    platform: str = Field(..., description="Operating system platform")
    cpu_count: int = Field(..., description="Number of CPU cores")
    memory_total: int = Field(..., description="Total memory in bytes")
    memory_available: int = Field(..., description="Available memory in bytes")
    disk_usage: Dict[str, Dict[str, int]] = Field(..., description="Disk usage by drive")
    uptime: float = Field(..., description="System uptime in seconds")


class DatabaseOperation(BaseModel):
    """Database operation request."""
    operation: str = Field(..., description="Operation type (select, insert, update, delete)")
    table: str = Field(..., description="Table name")
    data: Optional[Dict[str, Any]] = Field(None, description="Data for insert/update")
    where_clause: Optional[str] = Field(None, description="WHERE clause for select/update/delete")
    limit: Optional[int] = Field(None, ge=1, description="Result limit for select")


class DatabaseResult(BaseModel):
    """Database operation result."""
    success: bool = Field(..., description="Whether operation succeeded")
    affected_rows: int = Field(..., description="Number of affected rows")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Query results")
    message: str = Field(..., description="Result message")


# Integration status models
class IntegrationStatus(BaseModel):
    """System integration status."""
    file_system: bool = Field(..., description="File system integration available")
    process_control: bool = Field(..., description="Process control available")
    task_scheduling: bool = Field(..., description="Task scheduling available")
    database: bool = Field(..., description="Database integration available")
    system_monitoring: bool = Field(..., description="System monitoring available")


class AvailableIntegrations(BaseModel):
    """Available system integrations."""
    integrations: List[str] = Field(..., description="List of available integrations")
    status: IntegrationStatus = Field(..., description="Integration status")
    capabilities: Dict[str, List[str]] = Field(..., description="Capabilities by category")
