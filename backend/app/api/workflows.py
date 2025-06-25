from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
import json
import logging
from datetime import datetime

from ..workflow_manager import workflow_manager
from ..models.schemas import WorkflowCreateRequest, WorkflowResponse, WorkflowStatus
from ..mcp.client import MCPProjectClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])

# MCP 클라이언트 초기화는 함수 내에서 수행


@router.post("/", response_model=WorkflowResponse)
async def create_workflow(workflow_data: WorkflowCreateRequest, background_tasks: BackgroundTasks):
    """새로운 워크플로 생성"""
    try:
        # 입력 검증
        if not workflow_data.user_input or len(workflow_data.user_input.strip()) < 10:
            raise HTTPException(
                status_code=400, 
                detail="사용자 입력은 최소 10글자 이상이어야 합니다."
            )
        
        # 워크플로 시작
        workflow_id = await workflow_manager.start_workflow(workflow_data)
        
        return {
            "id": workflow_id,
            "project_name": workflow_data.project_name or "auto-generated",
            "user_input": workflow_data.user_input,
            "status": WorkflowStatus.RUNNING,
            "progress": 0,
            "current_agent": "pm",
            "created_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"워크플로 생성 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """워크플로 상태 조회"""
    try:
        status = await workflow_manager.get_workflow_status(workflow_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="워크플로를 찾을 수 없습니다.")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"워크플로 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{workflow_id}/stream")
async def stream_workflow_progress(workflow_id: str):
    """워크플로 진행상황 스트림"""
    try:
        # 워크플로 존재 확인
        status = await workflow_manager.get_workflow_status(workflow_id)
        if not status:
            raise HTTPException(status_code=404, detail="워크플로를 찾을 수 없습니다.")
        
        async def generate():
            async for progress in workflow_manager.get_workflow_progress_stream(workflow_id):
                # Server-Sent Events 형식으로 전송
                data = json.dumps(progress, ensure_ascii=False, default=str)
                yield f"data: {data}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"워크플로 스트림 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_workflows():
    """활성 워크플로 목록"""
    try:
        workflows = await workflow_manager.list_active_workflows()
        return {
            "workflows": workflows,
            "total": len(workflows)
        }
        
    except Exception as e:
        logger.error(f"워크플로 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}")
async def cancel_workflow(workflow_id: str):
    """워크플로 취소"""
    try:
        success = await workflow_manager.cancel_workflow(workflow_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="워크플로를 찾을 수 없습니다.")
        
        return {"message": "워크플로가 취소되었습니다."}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"워크플로 취소 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/summary")
async def get_workflow_statistics():
    """워크플로 통계"""
    try:
        stats = workflow_manager.get_workflow_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"워크플로 통계 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_workflows(max_age_hours: int = 24):
    """완료된 워크플로 정리"""
    try:
        cleaned_count = await workflow_manager.cleanup_completed_workflows(max_age_hours)
        return {
            "message": f"{cleaned_count}개의 워크플로가 정리되었습니다.",
            "cleaned_count": cleaned_count
        }
        
    except Exception as e:
        logger.error(f"워크플로 정리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))
