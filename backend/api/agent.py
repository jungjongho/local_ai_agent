"""
Agent API endpoints for tool-enabled AI interactions.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.agent_service import agent_service
from models.chat_models import ChatMessage
from utils.logger import logger

router = APIRouter(prefix="/api/agent", tags=["agent"])


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution."""
    tool_name: str = Field(..., description="Name of the tool to execute")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    session_id: Optional[str] = Field(None, description="Session ID for tracking")


class AgentChatRequest(BaseModel):
    """Request model for agent chat with tools."""
    messages: List[ChatMessage] = Field(..., description="Chat messages")
    session_id: Optional[str] = Field(None, description="Session ID for context")
    max_iterations: int = Field(5, ge=1, le=10, description="Maximum tool calling iterations")


class WebSearchRequest(BaseModel):
    """Simplified request for web search operations."""
    operation: str = Field(..., description="Web search operation to perform")
    query: str = Field(..., description="Search query or URL")
    search_engine: str = Field("duckduckgo", description="Search engine to use")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")
    extract_content: bool = Field(False, description="Whether to extract content from URLs")
    time_range: str = Field("all", description="Time range for search results")
    language: str = Field("en", description="Language for search results")


class FileOperationRequest(BaseModel):
    """Simplified request for file operations."""
    operation: str = Field(..., description="File operation to perform")
    path: str = Field(..., description="File or directory path")
    content: Optional[str] = Field(None, description="Content for write operations")
    destination: Optional[str] = Field(None, description="Destination for copy/move operations")
    pattern: Optional[str] = Field(None, description="Search pattern")
    recursive: bool = Field(False, description="Whether to operate recursively")
    encoding: str = Field("utf-8", description="File encoding")


@router.get("/tools")
async def get_available_tools() -> Dict[str, Any]:
    """
    Get list of available tools.
    
    Returns:
        List of available tools with their specifications
    """
    logger.info("Getting available tools")
    
    try:
        tools = agent_service.get_available_tools()
        return {
            "tools": tools,
            "count": len(tools),
            "enabled_count": len([t for t in tools if t["enabled"]])
        }
        
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tools: {str(e)}"
        )


@router.post("/execute")
async def execute_tool(request: ToolExecutionRequest) -> Dict[str, Any]:
    """
    Execute a specific tool.
    
    Args:
        request: Tool execution request
        
    Returns:
        Tool execution result
    """
    logger.info(f"Executing tool: {request.tool_name}")
    
    try:
        result = await agent_service.execute_tool(
            tool_name=request.tool_name,
            parameters=request.parameters,
            session_id=request.session_id
        )
        
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "execution_time": result.execution_time,
            "metadata": result.metadata
        }
        
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool execution failed: {str(e)}"
        )


@router.post("/chat")
async def agent_chat(request: AgentChatRequest) -> Dict[str, Any]:
    """
    Chat with AI agent that can use tools.
    
    Args:
        request: Agent chat request
        
    Returns:
        Agent response with tool usage details
    """
    logger.info(f"Agent chat with {len(request.messages)} messages")
    
    try:
        response = await agent_service.agent_chat_with_tools(
            messages=request.messages,
            session_id=request.session_id,
            max_iterations=request.max_iterations
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Agent chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent chat failed: {str(e)}"
        )


@router.post("/search")
async def web_search(request: WebSearchRequest) -> Dict[str, Any]:
    """
    Perform web search operations.
    
    Args:
        request: Web search request
        
    Returns:
        Web search result
    """
    logger.info(f"Web search: {request.operation} - {request.query}")
    
    try:
        # Prepare parameters
        parameters = {
            "operation": request.operation,
            "query": request.query,
            "search_engine": request.search_engine,
            "max_results": request.max_results,
            "extract_content": request.extract_content,
            "time_range": request.time_range,
            "language": request.language
        }
        
        result = await agent_service.execute_tool("web_search", parameters)
        
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "execution_time": result.execution_time,
            "operation": request.operation,
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Web search failed: {str(e)}"
        )



@router.post("/file")
async def file_operation(request: FileOperationRequest) -> Dict[str, Any]:
    """
    Perform file system operations.
    
    Args:
        request: File operation request
        
    Returns:
        File operation result
    """
    logger.info(f"File operation: {request.operation} on {request.path}")
    
    try:
        # Prepare parameters
        parameters = {
            "operation": request.operation,
            "path": request.path,
            "encoding": request.encoding,
            "recursive": request.recursive
        }
        
        # Add optional parameters
        if request.content is not None:
            parameters["content"] = request.content
        if request.destination is not None:
            parameters["destination"] = request.destination
        if request.pattern is not None:
            parameters["pattern"] = request.pattern
        
        result = await agent_service.simple_file_operation(**parameters)
        
        return {
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "execution_time": result.execution_time,
            "operation": request.operation,
            "path": request.path
        }
        
    except Exception as e:
        logger.error(f"File operation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File operation failed: {str(e)}"
        )


@router.get("/sessions/{session_id}")
async def get_session_info(session_id: str) -> Dict[str, Any]:
    """
    Get information about a specific session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session information
    """
    logger.debug(f"Getting session info: {session_id}")
    
    try:
        session_info = agent_service.get_session_info(session_id)
        
        if session_info is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session not found: {session_id}"
            )
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving session: {str(e)}"
        )


@router.get("/statistics")
async def get_agent_statistics() -> Dict[str, Any]:
    """
    Get comprehensive agent service statistics.
    
    Returns:
        Agent service statistics including tool usage
    """
    logger.debug("Getting agent statistics")
    
    try:
        stats = agent_service.get_tool_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting agent statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.post("/sessions/cleanup")
async def cleanup_sessions(max_age_hours: int = 24) -> Dict[str, Any]:
    """
    Clean up old inactive sessions.
    
    Args:
        max_age_hours: Maximum age in hours for sessions to keep
        
    Returns:
        Cleanup result
    """
    logger.info(f"Cleaning up sessions older than {max_age_hours} hours")
    
    try:
        sessions_before = len(agent_service.active_sessions)
        agent_service.cleanup_old_sessions(max_age_hours)
        sessions_after = len(agent_service.active_sessions)
        
        cleaned_up = sessions_before - sessions_after
        
        return {
            "sessions_before": sessions_before,
            "sessions_after": sessions_after,
            "cleaned_up": cleaned_up,
            "max_age_hours": max_age_hours
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Session cleanup failed: {str(e)}"
        )


@router.get("/health")
async def agent_health_check() -> Dict[str, Any]:
    """
    Perform health check on agent service.
    
    Returns:
        Agent service health status
    """
    logger.debug("Performing agent health check")
    
    try:
        health_status = await agent_service.health_check()
        
        if health_status["status"] == "unhealthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)}
        )


# Web search test endpoints
@router.post("/test/web-search")
async def test_web_search(query: str, search_engine: str = "duckduckgo") -> Dict[str, Any]:
    """
    Test endpoint for web search.
    
    Args:
        query: Search query
        search_engine: Search engine to use
        
    Returns:
        Search results
    """
    try:
        result = await agent_service.execute_tool(
            "web_search",
            {
                "operation": "search",
                "query": query,
                "search_engine": search_engine,
                "max_results": 5
            }
        )
        
        return {
            "success": result.success,
            "query": query,
            "search_engine": search_engine,
            "results": result.result.get("results", []) if result.success else [],
            "total_results": result.result.get("total_results", 0) if result.success else 0,
            "error": result.error,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Test web search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


@router.post("/test/extract-content")
async def test_extract_content(url: str) -> Dict[str, Any]:
    """
    Test endpoint for content extraction.
    
    Args:
        url: URL to extract content from
        
    Returns:
        Extracted content
    """
    try:
        result = await agent_service.execute_tool(
            "web_search",
            {
                "operation": "extract_content",
                "query": url
            }
        )
        
        return {
            "success": result.success,
            "url": url,
            "title": result.result.get("title", "") if result.success else "",
            "content_length": result.result.get("content_length", 0) if result.success else 0,
            "description": result.result.get("description", "") if result.success else "",
            "error": result.error,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Test content extraction error: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


@router.post("/test/validate-url")
async def test_validate_url(url: str) -> Dict[str, Any]:
    """
    Test endpoint for URL validation.
    
    Args:
        url: URL to validate
        
    Returns:
        URL validation result
    """
    try:
        result = await agent_service.execute_tool(
            "web_search",
            {
                "operation": "validate_url",
                "query": url
            }
        )
        
        return {
            "success": result.success,
            "url": url,
            "accessible": result.result.get("accessible", False) if result.success else False,
            "status_code": result.result.get("status_code", 0) if result.success else 0,
            "content_type": result.result.get("content_type", "") if result.success else "",
            "error": result.error,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Test URL validation error: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


# File system test endpoints (existing)
@router.post("/test/file-read")
async def test_file_read(file_path: str) -> Dict[str, Any]:
    """
    Test endpoint for reading files.
    
    Args:
        file_path: Path to file to read
        
    Returns:
        File content and metadata
    """
    try:
        result = await agent_service.simple_file_operation(
            operation="read",
            path=file_path
        )
        
        return {
            "success": result.success,
            "file_path": file_path,
            "content": result.result.get("content", "") if result.success else None,
            "size": result.result.get("size", 0) if result.success else 0,
            "error": result.error,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Test file read error: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@router.post("/test/file-write")
async def test_file_write(file_path: str, content: str) -> Dict[str, Any]:
    """
    Test endpoint for writing files.
    
    Args:
        file_path: Path to file to write
        content: Content to write
        
    Returns:
        Write operation result
    """
    try:
        result = await agent_service.simple_file_operation(
            operation="write",
            path=file_path,
            content=content
        )
        
        return {
            "success": result.success,
            "file_path": file_path,
            "size": result.result.get("size", 0) if result.success else 0,
            "error": result.error,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Test file write error: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


@router.get("/test/directory-list")
async def test_directory_list(dir_path: str = ".", recursive: bool = False) -> Dict[str, Any]:
    """
    Test endpoint for listing directories.
    
    Args:
        dir_path: Directory path to list
        recursive: Whether to list recursively
        
    Returns:
        Directory listing
    """
    try:
        result = await agent_service.simple_file_operation(
            operation="list",
            path=dir_path,
            recursive=recursive
        )
        
        return {
            "success": result.success,
            "directory": dir_path,
            "items": result.result.get("items", []) if result.success else [],
            "count": result.result.get("count", 0) if result.success else 0,
            "recursive": recursive,
            "error": result.error,
            "execution_time": result.execution_time
        }
        
    except Exception as e:
        logger.error(f"Test directory list error: {e}")
        return {
            "success": False,
            "error": str(e),
            "directory": dir_path
        }
