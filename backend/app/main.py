from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

from .core.config import settings
from .core.logging import setup_logging
from .api.workflows import router as workflows_router
from .api.projects import router as projects_router
from .api.models import router as models_router
from .models.database import init_db

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 이벤트"""
    # 시작 시
    logger.info("🚀 멀티 AI 에이전트 웹서비스 생성 시스템 시작")
    
    # 데이터베이스 초기화
    await init_db()
    logger.info("📊 데이터베이스 초기화 완료")
    
    # 작업 디렉토리 확인
    from .mcp.client import MCPManager
    import os
    workspace_path = os.path.join(os.getcwd(), "workspace", "generated_projects")
    mcp_manager = MCPManager(workspace_path)
    logger.info(f"📁 작업 공간: {workspace_path}")

    
    yield
    
    # 종료 시
    logger.info("🛑 멀티 AI 에이전트 웹서비스 생성 시스템 종료")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="멀티 AI 에이전트 웹서비스 생성 시스템",
    description="사용자 입력 한 줄로 완전한 웹서비스(React + FastAPI)를 자동 생성하는 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(workflows_router)
app.include_router(projects_router)
app.include_router(models_router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "멀티 AI 에이전트 웹서비스 생성 시스템",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    try:
        from .mcp.client import MCPProjectClient
        import os
        
        workspace_path = os.path.join(os.getcwd(), "workspace", "generated_projects")
        project_client = MCPProjectClient(workspace_path)
        projects = await project_client.list_projects()
        
        return {
            "status": "healthy",
            "timestamp": "2024-12-01T00:00:00Z",
            "workspace": {
                "exists": os.path.exists(workspace_path),
                "projects_count": len(projects)
            },
            "system": {
                "openai_configured": bool(settings.OPENAI_API_KEY),
                "workspace_dir": workspace_path
            }
        }
        
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/api/v1/status")
async def api_status():
    """API 상태"""
    try:
        from .workflow_manager import workflow_manager
        stats = workflow_manager.get_workflow_statistics()
        
        return {
            "api_version": "v1",
            "status": "operational",
            "features": {
                "workflow_management": True,
                "project_generation": True,
                "real_time_monitoring": True,
                "file_system_access": True,
                "docker_support": True
            },
            "agents": {
                "pm": "Project Manager",
                "uiux": "UI/UX Designer", 
                "frontend": "Frontend Developer",
                "backend": "Backend Developer",
                "devops": "DevOps Engineer"
            },
            "workflow_stats": stats
        }
        
    except Exception as e:
        logger.error(f"API 상태 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리기"""
    logger.error(f"예상치 못한 오류: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "내부 서버 오류가 발생했습니다.",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "서버 오류"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
