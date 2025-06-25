from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class WorkflowStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    PM = "pm"
    UIUX = "uiux"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"


class WorkflowCreateRequest(BaseModel):
    """워크플로 생성 요청"""
    user_input: str = Field(..., description="사용자 입력 요구사항")
    project_name: Optional[str] = Field(None, description="프로젝트 이름 (자동 생성 가능)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "온라인 할일 관리 앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해.",
                "project_name": "todo-app"
            }
        }


class WorkflowResponse(BaseModel):
    """워크플로 응답"""
    id: str
    project_name: str
    user_input: str
    status: WorkflowStatus
    current_agent: Optional[str] = None
    progress: int = 0
    
    planning_result: Optional[Dict[str, Any]] = None
    uiux_result: Optional[Dict[str, Any]] = None
    frontend_result: Optional[Dict[str, Any]] = None
    backend_result: Optional[Dict[str, Any]] = None
    devops_result: Optional[Dict[str, Any]] = None
    
    project_path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class AgentResult(BaseModel):
    """에이전트 실행 결과"""
    agent_name: str
    status: str
    result: Dict[str, Any]
    error: Optional[str] = None
    execution_time: Optional[float] = None
    tokens_used: Optional[int] = None


class ProjectStructure(BaseModel):
    """생성된 프로젝트 구조"""
    project_name: str
    project_path: str
    frontend_url: Optional[str] = None
    backend_url: Optional[str] = None
    files_created: List[str] = []
    is_running: bool = False


class WebSocketMessage(BaseModel):
    """WebSocket 메시지"""
    type: str  # progress, error, completed
    workflow_id: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class ProgressUpdate(BaseModel):
    """진행상황 업데이트"""
    workflow_id: str
    current_agent: str
    progress: int
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorMessage(BaseModel):
    """오류 메시지"""
    workflow_id: str
    agent_name: str
    error_type: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.now)


# PM Agent 관련 스키마
class RequirementAnalysis(BaseModel):
    """요구사항 분석 결과"""
    project_type: str
    main_features: List[str]
    technical_requirements: List[str]
    ui_requirements: List[str]
    data_models: List[Dict[str, Any]]
    api_endpoints: List[Dict[str, Any]]


class ProjectPlan(BaseModel):
    """프로젝트 계획"""
    project_name: str
    description: str
    tech_stack: Dict[str, str]
    requirements: RequirementAnalysis
    estimated_complexity: str  # simple, medium, complex
    estimated_time: str


# UI/UX Agent 관련 스키마
class ComponentDesign(BaseModel):
    """컴포넌트 설계"""
    name: str
    type: str
    props: List[str]
    styling: Dict[str, Any]
    functionality: str


class UIDesign(BaseModel):
    """UI 설계"""
    theme: Dict[str, Any]
    components: List[ComponentDesign]
    layouts: List[Dict[str, Any]]
    navigation: Dict[str, Any]


# Frontend Agent 관련 스키마
class ReactComponent(BaseModel):
    """React 컴포넌트"""
    name: str
    file_path: str
    code: str
    dependencies: List[str]


class FrontendStructure(BaseModel):
    """프론트엔드 구조"""
    components: List[ReactComponent]
    pages: List[ReactComponent]
    services: List[Dict[str, Any]]
    package_json: Dict[str, Any]


# Backend Agent 관련 스키마
class APIEndpoint(BaseModel):
    """API 엔드포인트"""
    path: str
    method: str
    function_name: str
    parameters: List[Dict[str, Any]]
    response_model: str


class BackendStructure(BaseModel):
    """백엔드 구조"""
    models: List[Dict[str, Any]]
    endpoints: List[APIEndpoint]
    database_config: Dict[str, Any]
    dependencies: List[str]


# DevOps Agent 관련 스키마
class DeploymentConfig(BaseModel):
    """배포 설정"""
    docker_compose: str
    environment_files: Dict[str, str]
    scripts: Dict[str, str]
    ports: Dict[str, int]
