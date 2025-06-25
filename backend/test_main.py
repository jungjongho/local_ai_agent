"""
임시 테스트용 FastAPI 애플리케이션

복잡한 에이전트 시스템 대신 기본적인 API만 제공하여
시스템이 정상 동작하는지 확인합니다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="멀티 AI 에이전트 웹서비스 생성 시스템 (테스트 모드)",
    description="테스트용 간단한 API 서버",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 임시 데이터 저장소
mock_projects = [
    {
        "name": "todo-app-demo",
        "created_at": int(datetime.now().timestamp()),
        "status": "completed",
        "has_docker": True,
        "has_scripts": True,
        "has_readme": True,
        "description": "할일 관리 애플리케이션 데모"
    },
    {
        "name": "blog-system",
        "created_at": int(datetime.now().timestamp()) - 3600,
        "status": "completed", 
        "has_docker": True,
        "has_scripts": True,
        "has_readme": True,
        "description": "간단한 블로그 시스템"
    }
]

mock_workflows = [
    {
        "id": "wf001",
        "status": "completed",
        "created_at": int(datetime.now().timestamp()),
        "project_name": "todo-app-demo"
    },
    {
        "id": "wf002", 
        "status": "running",
        "created_at": int(datetime.now().timestamp()) - 1800,
        "project_name": "blog-system"
    }
]

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "멀티 AI 에이전트 웹서비스 생성 시스템 (테스트 모드)",
        "version": "1.0.0-test",
        "docs": "/docs",
        "status": "running",
        "mode": "test"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    workspace_path = os.path.join(os.getcwd(), "workspace", "generated_projects")
    os.makedirs(workspace_path, exist_ok=True)
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "workspace": {
            "exists": os.path.exists(workspace_path),
            "projects_count": len(mock_projects)
        },
        "system": {
            "openai_configured": os.getenv("OPENAI_API_KEY") is not None,
            "workspace_dir": workspace_path
        }
    }

@app.get("/api/v1/status")
async def api_status():
    """API 상태"""
    return {
        "api_version": "v1",
        "status": "operational",
        "mode": "test",
        "features": {
            "workflow_management": True,
            "project_generation": True,
            "real_time_monitoring": False,  # 테스트 모드에서는 비활성화
            "file_system_access": True,
            "docker_support": True
        },
        "agents": {
            "pm": "Project Manager (Mock)",
            "uiux": "UI/UX Designer (Mock)", 
            "frontend": "Frontend Developer (Mock)",
            "backend": "Backend Developer (Mock)",
            "devops": "DevOps Engineer (Mock)"
        },
        "workflow_stats": {
            "total": len(mock_workflows),
            "completed": len([w for w in mock_workflows if w["status"] == "completed"]),
            "running": len([w for w in mock_workflows if w["status"] == "running"]),
            "failed": 0
        }
    }

@app.get("/api/v1/projects/")
async def list_projects():
    """프로젝트 목록 조회"""
    return {
        "projects": mock_projects,
        "total": len(mock_projects)
    }

@app.get("/api/v1/projects/{project_name}")
async def get_project(project_name: str):
    """특정 프로젝트 조회"""
    project = next((p for p in mock_projects if p["name"] == project_name), None)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다")
    
    return {
        **project,
        "files": [
            "frontend/src/App.tsx",
            "frontend/package.json", 
            "backend/main.py",
            "backend/requirements.txt",
            "docker-compose.yml",
            "README.md"
        ],
        "logs": [
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "프로젝트 생성 완료"},
            {"timestamp": datetime.now().isoformat(), "level": "INFO", "message": "Docker 설정 완료"}
        ]
    }

@app.post("/api/v1/workflows/")
async def create_workflow(workflow_data: Dict[str, Any]):
    """새 워크플로 생성"""
    user_input = workflow_data.get("user_input", "")
    project_name = workflow_data.get("project_name", f"project-{len(mock_workflows) + 1}")
    
    if not user_input:
        raise HTTPException(status_code=400, detail="user_input이 필요합니다")
    
    # 새 워크플로 생성 (모의)
    new_workflow = {
        "id": f"wf{len(mock_workflows) + 1:03d}",
        "status": "running",
        "created_at": int(datetime.now().timestamp()),
        "project_name": project_name,
        "user_input": user_input,
        "progress": 0
    }
    
    mock_workflows.append(new_workflow)
    
    logger.info(f"새 워크플로 생성: {new_workflow['id']} - {user_input}")
    
    return {
        "workflow_id": new_workflow["id"],
        "status": "started",
        "message": f"워크플로가 시작되었습니다: {project_name}",
        "project_name": project_name
    }

@app.get("/api/v1/workflows/")
async def list_workflows():
    """워크플로 목록 조회"""
    return {
        "workflows": mock_workflows,
        "total": len(mock_workflows)
    }

@app.get("/api/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """특정 워크플로 조회"""
    workflow = next((w for w in mock_workflows if w["id"] == workflow_id), None)
    if not workflow:
        raise HTTPException(status_code=404, detail="워크플로를 찾을 수 없습니다")
    
    return workflow

@app.get("/api/v1/workflows/statistics")
async def get_workflow_statistics():
    """워크플로 통계"""
    status_breakdown = {}
    for workflow in mock_workflows:
        status = workflow["status"]
        status_breakdown[status] = status_breakdown.get(status, 0) + 1
    
    return {
        "total_workflows": len(mock_workflows),
        "status_breakdown": status_breakdown,
        "recent_workflows": mock_workflows[-5:] if len(mock_workflows) > 5 else mock_workflows
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    logger.error(f"예상치 못한 오류: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "내부 서버 오류가 발생했습니다",
            "detail": str(exc),
            "mode": "test"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 테스트 모드로 백엔드 서버를 시작합니다...")
    uvicorn.run(
        "test_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
