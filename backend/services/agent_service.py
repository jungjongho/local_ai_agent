"""
개선된 Agent service - 실용적이면서 안전한 파일 시스템 접근
"""
import asyncio
import json
import uuid
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
import os

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


class ImprovedAgentService:
    """
    개선된 Agent service - 더 실용적인 파일 시스템 접근을 제공합니다.
    
    주요 개선사항:
    1. 프로젝트 루트 디렉토리 접근 허용
    2. 사용자 홈 디렉토리 내 안전한 접근
    3. 화이트리스트 기반 보안 정책
    4. 명확한 에러 메시지와 로깅
    """
    
    def __init__(self):
        self.config = AgentConfig()
        self.tools: Dict[str, BaseTool] = {}
        self.active_sessions: Dict[str, AgentSession] = {}
        
        # 프로젝트 루트 경로 계산
        self.project_root = Path(__file__).parent.parent.parent.resolve()
        
        # Initialize improved tools
        self._initialize_improved_tools()
        
        logger.info(f"ImprovedAgentService initialized with project root: {self.project_root}")
    
    def _get_safe_allowed_paths(self) -> List[str]:
        """
        안전하면서도 실용적인 허용 경로 리스트를 생성합니다.
        
        설계 원칙:
        1. 프로젝트 디렉토리 전체 접근 허용 (개발 편의성)
        2. 사용자 Desktop, Documents 하위 작업 디렉토리 허용
        3. 시스템 중요 디렉토리는 차단
        4. 환경에 따른 동적 경로 설정
        """
        allowed_paths = []
        
        # 1. 프로젝트 루트 디렉토리 (가장 중요)
        allowed_paths.append(str(self.project_root))
        
        # 2. 사용자 홈 디렉토리의 안전한 영역들
        home_dir = Path.home()
        safe_home_paths = [
            home_dir / "Desktop",
            home_dir / "Documents", 
            home_dir / "Downloads",
            home_dir / "workspace",
            home_dir / "projects"
        ]
        
        for path in safe_home_paths:
            if path.exists():
                allowed_paths.append(str(path))
        
        # 3. 프로젝트별 작업 디렉토리들
        project_work_dirs = [
            self.project_root / "data",
            self.project_root / "workspace", 
            self.project_root / "temp",
            self.project_root / "outputs"
        ]
        
        for work_dir in project_work_dirs:
            work_dir.mkdir(parents=True, exist_ok=True)
            allowed_paths.append(str(work_dir))
        
        # 4. 개발환경에서 추가 허용 경로 (선택적)
        if os.getenv("DEVELOPMENT_MODE", "false").lower() == "true":
            # 개발 모드에서는 더 넓은 접근 허용
            current_working_dir = Path.cwd()
            allowed_paths.append(str(current_working_dir))
        
        logger.info(f"Configured {len(allowed_paths)} allowed paths for file operations")
        return allowed_paths
    
    def _get_blocked_patterns(self) -> List[str]:
        """
        보안을 위한 차단 패턴 정의.
        """
        return [
            "/System/",
            "/usr/bin/", 
            "/bin/",
            "/sbin/",
            "/etc/passwd",
            "/etc/shadow",
            "/.ssh/",
            "/root/",
            "C:\\Windows\\System32",
            "C:\\Program Files",
            "__pycache__",
            ".git/objects",
            "node_modules"
        ]
    
    def _initialize_improved_tools(self):
        """Initialize tools with improved, practical configurations."""
        try:
            # 개선된 파일 시스템 도구 설정
            fs_config = FileSystemConfig(
                safe_mode=True,
                allowed_paths=self._get_safe_allowed_paths(),
                blocked_patterns=self._get_blocked_patterns(),
                max_file_size=50 * 1024 * 1024,  # 50MB limit (개발 작업에 충분)
                enable_backup=True,
                backup_directory=str(self.project_root / "data" / "backups"),
                # 텍스트 파일과 개발 파일들에 대한 확장된 허용 목록
                allowed_extensions=[
                    '.txt', '.md', '.json', '.csv', '.xml', '.yml', '.yaml',
                    '.py', '.js', '.html', '.css', '.sql', '.log', '.ini',
                    '.conf', '.cfg', '.env', '.gitignore', '.dockerfile',
                    '.sh', '.bat', '.ps1'  # 스크립트 파일들도 허용
                ],
                blocked_extensions=[
                    '.exe', '.dll', '.so', '.dylib', '.app', '.deb', '.rpm',
                    '.msi', '.pkg', '.dmg', '.iso'  # 실행파일과 패키지들만 차단
                ]
            )
            
            self.tools["file_system"] = FileSystemTool(fs_config)
            
            # 웹 검색 도구는 기존 설정 유지 (이미 안전함)
            web_config = WebSearchConfig(
                safe_mode=True,
                max_results=10,
                timeout=30,
                enable_caching=True,
                blocked_domains=["malware.com", "phishing.com"],
                max_content_length=50000
            )
            
            self.tools["web_search"] = WebSearchTool(web_config)
            
            logger.info(f"Successfully initialized {len(self.tools)} tools with improved configurations")
            
            # 설정 정보 로깅 (디버깅 목적)
            for tool_name, tool in self.tools.items():
                if hasattr(tool, 'fs_config'):
                    logger.info(f"Tool '{tool_name}' allows {len(tool.fs_config.allowed_paths)} paths")
            
        except Exception as e:
            logger.error(f"Failed to initialize improved tools: {e}")
            raise
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools with their specifications."""
        tools_info = []
        
        for tool in self.tools.values():
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema,
                "enabled": tool.config.enabled,
                "statistics": tool.get_statistics()
            }
            
            # 파일 시스템 도구의 경우 허용된 경로 정보 추가
            if hasattr(tool, 'fs_config') and tool.fs_config.allowed_paths:
                tool_info["allowed_paths_count"] = len(tool.fs_config.allowed_paths)
                tool_info["sample_allowed_paths"] = tool.fs_config.allowed_paths[:3]  # 처음 3개만 보여줌
            
            tools_info.append(tool_info)
        
        return tools_info
    
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
        개선된 에러 메시지와 더 나은 로깅을 제공합니다.
        """
        if tool_name not in self.tools:
            error_msg = f"Tool not found: {tool_name}. Available tools: {list(self.tools.keys())}"
            logger.error(error_msg)
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=0.0
            )
        
        tool = self.tools[tool_name]
        
        # Check if tool is allowed
        if tool_name not in self.config.allowed_tools:
            error_msg = f"Tool not allowed: {tool_name}. Allowed tools: {self.config.allowed_tools}"
            logger.error(error_msg)
            return ToolResult(
                success=False,
                error=error_msg,
                execution_time=0.0
            )
        
        # Get or create session
        session = self._get_or_create_session(session_id)
        
        logger.info(
            f"Executing tool: {tool_name}",
            session_id=session.session_id,
            parameters=parameters
        )
        
        # 파일 경로 관련 매개변수 로깅 (디버깅 도움)
        if 'path' in parameters:
            logger.info(f"Target path: {parameters['path']}")
            
            # 경로 접근 가능성 사전 검사
            if hasattr(tool, 'fs_config'):
                target_path = Path(parameters['path']).resolve()
                allowed = False
                for allowed_path in tool.fs_config.allowed_paths:
                    try:
                        if target_path.is_relative_to(Path(allowed_path).resolve()):
                            allowed = True
                            logger.info(f"Path access granted via allowed path: {allowed_path}")
                            break
                    except (ValueError, OSError):
                        continue
                
                if not allowed:
                    logger.warning(f"Path access may be denied: {target_path}")
                    logger.info(f"Allowed paths: {tool.fs_config.allowed_paths}")
        
        try:
            # Execute tool
            result = await tool.execute(**parameters)
            
            # Update session
            session.total_tool_executions += 1
            if result.success:
                session.successful_executions += 1
                logger.info(f"Tool execution successful: {tool_name}")
            else:
                logger.warning(f"Tool execution failed: {tool_name}, Error: {result.error}")
            
            session.last_activity = datetime.now()
            session.tool_calls.append({
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result.dict(),
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            error_msg = f"Tool execution error for {tool_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return ToolResult(
                success=False,
                error=error_msg,
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
        파일 작업을 더 적극적으로 수행하도록 시스템 메시지 개선.
        """
        session = self._get_or_create_session(session_id)
        
        # Prepare messages for function calling
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Get available functions
        functions = self.get_tool_function_specs()
        
        # 개선된 시스템 메시지 - 더 적극적인 도구 사용 권장
        if functions and len(functions) > 0:
            has_system_message = any(msg.get("role") == "system" for msg in message_dicts)
            
            if not has_system_message:
                tool_descriptions = []
                for tool in functions:
                    tool_descriptions.append(f"- {tool['name']}: {tool['description']}")
                
                system_message = {
                    "role": "system",
                    "content": f"""You are a helpful AI assistant with active file system and web search capabilities.

Available tools:
{chr(10).join(tool_descriptions)}

**Important guidelines:**
1. **BE PROACTIVE**: When users ask you to create, read, or modify files, USE the file_system tool immediately
2. **HELP USERS DIRECTLY**: Don't just explain how they could do something - do it for them using tools
3. **PRACTICAL APPROACH**: If a user asks you to write content to a file, use the file_system tool to actually create/write the file
4. **ACCESSIBILITY**: You can access files in the project directory and user's common work areas (Desktop, Documents, etc.)

Examples of when to use tools:
- "Create a file with content X" → Use file_system tool to write the file
- "Read file Y" → Use file_system tool to read and return content  
- "Search for information about Z" → Use web_search tool to find current information
- "Save this data to a file" → Use file_system tool to write the data

Always try to complete the user's task using available tools rather than just providing instructions."""
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
                        
                        # If tool failed, provide helpful error context
                        if not tool_result.success:
                            logger.warning(f"Tool execution failed: {tool_result.error}")
                            # Continue rather than break - let AI handle the error
                
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
                        f"Agent chat completed successfully",
                        session_id=session.session_id,
                        iterations=iteration,
                        tools_used=len(tool_calls_made)
                    )
                    
                    return final_response
                
            except Exception as e:
                logger.error(f"Error in agent chat iteration {iteration}: {e}", exc_info=True)
                break
        
        # If we reach here, we hit max iterations or an error
        return {
            "response": "I've completed the available tool interactions. Some operations may have reached the iteration limit.",
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
        더 나은 에러 메시지와 로깅을 제공합니다.
        """
        parameters = {
            "operation": operation,
            "path": path,
            **kwargs
        }
        
        logger.info(f"Simple file operation requested: {operation} on {path}")
        
        return await self.execute_tool("file_system", parameters)
    
    def _get_or_create_session(self, session_id: str = None) -> AgentSession:
        """Get existing session or create new one."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = AgentSession(session_id)
            logger.info(f"Created new session: {session_id}")
        
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
                "tools_enabled": len([t for t in self.tools.values() if t.config.enabled]),
                "project_root": str(self.project_root)
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent service."""
        try:
            # Test file system tool with project directory
            fs_test_result = await self.simple_file_operation(
                operation="info",
                path=str(self.project_root)
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
                "project_root": str(self.project_root),
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


# Global agent service instance - using improved version
agent_service = ImprovedAgentService()
