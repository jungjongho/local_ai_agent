from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from ..mcp.client import MCPProjectClient
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/projects", tags=["projects"])
workspace_path = os.path.join(os.getcwd(), "workspace", "generated_projects")
mcp_project_client = MCPProjectClient(workspace_path)


@router.get("/")
async def list_projects():
    """생성된 프로젝트 목록 조회"""
    try:
        projects = await mcp_project_client.list_projects()
        return {
            "projects": projects,
            "total": len(projects)
        }
        
    except Exception as e:
        logger.error(f"프로젝트 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}")
async def get_project_info(project_id: str):
    """프로젝트 정보 조회"""
    try:
        project_info = await mcp_project_client.get_project_detail(project_id)
        
        if not project_info:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
        
        return project_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/start")
async def start_project(project_id: str):
    """프로젝트 개발 서버 시작"""
    try:
        result = await mcp_project_client.start_project_services(project_id)
        
        if result["success"]:
            return {
                "message": "개발 서버가 시작되었습니다.",
                "frontend_url": result.get("frontend_url"),
                "backend_url": result.get("backend_url"),
                "project_id": project_id
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "서버 시작 실패"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/stop")
async def stop_project(project_id: str):
    """프로젝트 개발 서버 중지"""
    try:
        result = await mcp_project_client.stop_project_services(project_id)
        
        if result["success"]:
            return {"message": result.get("message", "개발 서버가 중지되었습니다.")}
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "서버 중지 실패"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 중지 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """프로젝트 삭제"""
    try:
        success = await mcp_project_client.delete_project(project_id)
        
        if success:
            return {"message": "프로젝트가 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"프로젝트 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/logs")
async def get_project_logs(project_id: str):
    """프로젝트 로그 조회"""
    try:
        result = await mcp_project_client.get_project_logs(project_id)
        
        if result["success"]:
            return result["logs"]
        else:
            raise HTTPException(status_code=404, detail=result.get("error", "로그를 찾을 수 없습니다."))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspace/info")
async def get_workspace_info():
    """작업 공간 정보"""
    try:
        projects = await mcp_project_client.list_projects()
        return {
            "workspace_path": workspace_path,
            "projects_count": len(projects),
            "exists": os.path.exists(workspace_path)
        }
        
    except Exception as e:
        logger.error(f"작업 공간 정보 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workspace/requirements")
async def check_system_requirements():
    """시스템 요구사항 확인"""
    try:
        import shutil
        
        requirements = {
            "python": shutil.which("python3") is not None or shutil.which("python") is not None,
            "node": shutil.which("node") is not None,
            "npm": shutil.which("npm") is not None,
            "docker": shutil.which("docker") is not None,
            "git": shutil.which("git") is not None,
            "workspace_writable": os.access(workspace_path, os.W_OK) if os.path.exists(workspace_path) else True
        }
        
        return {
            "requirements": requirements,
            "all_satisfied": all(requirements.values()),
            "missing": [k for k, v in requirements.items() if not v]
        }
        
    except Exception as e:
        logger.error(f"시스템 요구사항 확인 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
