"""
Agent service for managing AI agents and tools.
Provides the foundation for Phase 2 agent functionality.
"""
import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from tools import FileSystemTool, WebSearchTool, BaseTool, ToolResult
from tools.base_tool import ToolConfig
from tools.file_system_tool import FileSystemConfig
from tools.web_search_tool import WebSearchConfig
from core.gpt_client import gpt_client
from core.error_handler import error_handler
from models.chat_models import ChatMessage
from utils.logger import logger


class AgentConfig:
    """Configuration for agent behavior."""
    def __init__(self):
        self.max_tool_execution_time = 60.0
        self.max_tools_per_request = 5
        self.enable_tool_chaining = True
        self.safe_mode = True
        self.allowed_tools = ["file_system", "web_search"]


class AgentSession:
    """Represents an agent session with context and tool usage history."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.tool_calls: List[Dict] = []
        self.context: Dict[str, Any] = {}
        self.total_tool_executions = 0
        self.successful_executions = 0


class AgentService:
    """
    Agent service that manages AI agents and their tools.
    
    This service provides the foundation for Phase 2 functionality,
    allowing agents to use various tools to interact with the system.
    """
    
    def __init__(self):
        self.config = AgentConfig()
        self.tools: Dict[str, BaseTool] = {}
        self.active_sessions: Dict[str, AgentSession] = {}
        
        # Initialize default tools
        self._initialize_tools()
        
        logger.info("AgentService initialized")
    
    def _initialize_tools(self):
        """Initialize available tools."""
        try:
            # Initialize file system tool with safe configuration
            fs_config = FileSystemConfig(
                safe_mode=True,
                allowed_paths=["data/workspace", "data/temp"],  # Restricted paths
                max_file_size=10 * 1024 * 1024,  # 10MB limit
                enable_backup=True
            )
            
            self.tools["file_system"] = FileSystemTool(fs_config)
            
            # Initialize web search tool with safe configuration
            web_config = WebSearchConfig(
                safe_mode=True,
                max_results=10,
                timeout=30,
                enable_caching=True,
                blocked_domains=["malware.com", "phishing.com"],
                max_content_length=50000  # 50KB limit
            )
            
            self.tools["web_search"] = WebSearchTool(web_config)
            
            logger.info(f"Initialized {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their specifications."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema,
                "enabled": tool.config.enabled,
                "statistics": tool.get_statistics()
            }
            for tool in self.tools.values()
        ]
    
    def get_tool_function_specs(self) -> List[Dict[str, Any]]:
        """Get OpenAI function specifications for all tools."""
        return [
            tool.to_function_spec() 
            for tool in self.tools.values() 
            if tool.config.enabled
        ]
    
    async def execute_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any],
        session_id: str = None
    ) -> ToolResult:
        """
        Execute a specific tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            session_id: Optional session ID for tracking
            
        Returns:
            ToolResult with execution details
        """
        if tool_name not in self.tools:
            return ToolResult(
                success=False,
                error=f"Tool not found: {tool_name}",
                execution_time=0.0
            )
        
        tool = self.tools[tool_name]
        
        # Check if tool is allowed
        if tool_name not in self.config.allowed_tools:
            return ToolResult(
                success=False,
                error=f"Tool not allowed: {tool_name}",
                execution_time=0.0
            )
        
        # Get or create session
        session = self._get_or_create_session(session_id)
        
        logger.info(
            f"Executing tool: {tool_name}",
            session_id=session.session_id,
            parameters=parameters
        )
        
        try:
            # Execute tool
            result = await tool.execute(**parameters)
            
            # Update session
            session.total_tool_executions += 1
            if result.success:
                session.successful_executions += 1
            
            session.last_activity = datetime.now()
            session.tool_calls.append({
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result.dict(),
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ToolResult(
                success=False,
                error=f"Tool execution error: {str(e)}",
                execution_time=0.0
            )
    
    async def agent_chat_with_tools(
        self,
        messages: List[ChatMessage],
        session_id: str = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Enhanced chat that can use tools when needed.
        
        Args:
            messages: Chat messages
            session_id: Session identifier
            max_iterations: Maximum tool calling iterations
            
        Returns:
            Enhanced chat response with tool usage
        """
        session = self._get_or_create_session(session_id)
        
        # Prepare messages for function calling
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Get available functions
        functions = self.get_tool_function_specs()
        
        # Add system message to encourage tool usage
        if functions and len(functions) > 0:
            # Check if there's already a system message
            has_system_message = any(msg.get("role") == "system" for msg in message_dicts)
            
            if not has_system_message:
                # Add system message to encourage tool usage
                tool_descriptions = []
                for tool in functions:
                    tool_descriptions.append(f"- {tool['name']}: {tool['description']}")
                
                system_message = {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant with access to the following tools:

{chr(10).join(tool_descriptions)}

When a user asks you to perform tasks that can be accomplished with these tools, you should use them actively. For example:
- If asked to create, read, or modify files, use the file_system tool
- If asked to search for information online, use the web_search tool
- Always try to help the user by using the appropriate tools rather than just explaining how they could do it themselves.

Be proactive in using tools to complete tasks for the user."""
                }
                
                message_dicts.insert(0, system_message)
        
        iteration = 0
        tool_calls_made = []
        
        logger.info(
            f"Starting agent chat with {len(functions)} available tools",
            session_id=session.session_id
        )
        
        while iteration < max_iterations:
            try:
                # Make chat completion with function calling
                response = await gpt_client.chat_completion(
                    messages=message_dicts,
                    tools=[{"type": "function", "function": func} for func in functions] if functions else None,
                    tool_choice="auto" if functions else None,
                    use_cache=False  # Disable caching for tool-enabled chat
                )
                
                choice = response["choices"][0]
                message = choice["message"]
                
                # Check if AI wants to call a function
                if message.get("tool_calls"):
                    # Handle new tool_calls format
                    for tool_call in message["tool_calls"]:
                        function_call = tool_call["function"]
                        function_name = function_call["name"]
                        
                        try:
                            function_args = json.loads(function_call["arguments"])
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid function arguments: {e}")
                            break
                        
                        logger.info(f"AI requesting tool: {function_name}", args=function_args)
                        
                        # Execute the tool
                        tool_result = await self.execute_tool(
                            function_name,
                            function_args,
                            session.session_id
                        )
                        
                        tool_calls_made.append({
                            "tool": function_name,
                            "arguments": function_args,
                            "result": tool_result.dict()
                        })
                        
                        # Add tool call and result to conversation
                        message_dicts.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": message["tool_calls"]
                        })
                        
                        message_dicts.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": json.dumps(tool_result.dict())
                        })
                        
                        iteration += 1
                        
                        # If tool failed, break the loop
                        if not tool_result.success:
                            logger.warning(f"Tool execution failed: {tool_result.error}")
                            break
                
                else:
                    # AI provided a regular response, we're done
                    final_response = {
                        "response": message["content"],
                        "tool_calls": tool_calls_made,
                        "iterations": iteration,
                        "session_id": session.session_id,
                        "usage": response.get("usage", {}),
                        "total_tools_available": len(functions)
                    }
                    
                    logger.info(
                        f"Agent chat completed",
                        session_id=session.session_id,
                        iterations=iteration,
                        tools_used=len(tool_calls_made)
                    )
                    
                    return final_response
                
            except Exception as e:
                logger.error(f"Error in agent chat iteration {iteration}: {e}")
                break
        
        # If we reach here, we hit max iterations or an error
        return {
            "response": "I encountered an issue while processing your request with tools.",
            "tool_calls": tool_calls_made,
            "iterations": iteration,
            "session_id": session.session_id,
            "error": "Max iterations reached or execution error",
            "total_tools_available": len(functions)
        }
    
    async def simple_file_operation(
        self,
        operation: str,
        path: str,
        **kwargs
    ) -> ToolResult:
        """
        Simplified interface for common file operations.
        
        Args:
            operation: File operation (read, write, list, etc.)
            path: File path
            **kwargs: Additional parameters
            
        Returns:
            ToolResult
        """
        parameters = {
            "operation": operation,
            "path": path,
            **kwargs
        }
        
        return await self.execute_tool("file_system", parameters)
    
    def _get_or_create_session(self, session_id: str = None) -> AgentSession:
        """Get existing session or create new one."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = AgentSession(session_id)
        
        return self.active_sessions[session_id]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "total_tool_executions": session.total_tool_executions,
            "successful_executions": session.successful_executions,
            "success_rate": (
                session.successful_executions / session.total_tool_executions * 100
                if session.total_tool_executions > 0 else 0
            ),
            "tool_calls_count": len(session.tool_calls),
            "context_keys": list(session.context.keys())
        }
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove old inactive sessions."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            age_hours = (current_time - session.last_activity).total_seconds() / 3600
            if age_hours > max_age_hours:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get comprehensive tool usage statistics."""
        tool_stats = {}
        
        for tool_name, tool in self.tools.items():
            tool_stats[tool_name] = tool.get_statistics()
        
        # Session statistics
        total_sessions = len(self.active_sessions)
        active_sessions = sum(
            1 for session in self.active_sessions.values()
            if (datetime.now() - session.last_activity).total_seconds() < 3600
        )
        
        total_tool_calls = sum(
            session.total_tool_executions 
            for session in self.active_sessions.values()
        )
        
        return {
            "tools": tool_stats,
            "sessions": {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_tool_calls": total_tool_calls
            },
            "service_stats": {
                "tools_available": len(self.tools),
                "tools_enabled": len([t for t in self.tools.values() if t.config.enabled])
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent service."""
        try:
            # Test file system tool
            fs_test_result = await self.simple_file_operation(
                operation="info",
                path="."
            )
            
            # Test web search tool
            web_test_result = await self.execute_tool(
                "web_search",
                {"operation": "validate_url", "query": "https://httpbin.org/status/200"}
            )
            
            tools_healthy = fs_test_result.success and web_test_result.success
            
            return {
                "status": "healthy" if tools_healthy else "degraded",
                "tools_available": len(self.tools),
                "tools_enabled": len([t for t in self.tools.values() if t.config.enabled]),
                "active_sessions": len(self.active_sessions),
                "test_results": {
                    "file_system": fs_test_result.success,
                    "web_search": web_test_result.success
                }
            }
            
        except Exception as e:
            logger.error(f"Agent service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Global agent service instance
agent_service = AgentService()
