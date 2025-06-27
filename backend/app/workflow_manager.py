from typing import Dict, Any, List, Optional, AsyncGenerator
import asyncio
import json
import logging
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import uuid

from .agents.pm_agent import PMAgent
from .agents.uiux_agent import UIUXAgent
from .agents.frontend_agent import FrontendAgent
from .agents.backend_agent import BackendAgent
from .agents.devops_agent import DevOpsAgent
from .models.database import get_db_session
from .models.schemas import WorkflowCreateRequest, WorkflowStatus
from .mcp.client import MCPManager
from .core.config import settings

logger = logging.getLogger(__name__)


class WorkflowStage(Enum):
    """워크플로 단계"""
    PLANNING = "planning"
    UIUX_DESIGN = "uiux_design"
    FRONTEND_DEV = "frontend_dev"
    BACKEND_DEV = "backend_dev"
    DEVOPS_SETUP = "devops_setup"
    FILE_GENERATION = "file_generation"
    PROJECT_DEPLOYMENT = "project_deployment"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class WorkflowProgress:
    """워크플로 진행상황"""
    workflow_id: str
    stage: WorkflowStage
    progress_percentage: int
    current_agent: str
    message: str
    timestamp: datetime
    stage_results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class WorkflowManager:
    """멀티 AI 에이전트 워크플로 관리자"""
    
    def __init__(self):
        # 대기 중인 기본 모델 - 모델은 워크플로 생성 시 지정
        self.agents_cache = {}
        import os
        workspace_path = os.path.join(os.getcwd(), "workspace", "generated_projects")
        self.mcp_manager = MCPManager(workspace_path)
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        
        # 워크플로 단계별 진행률
        self.stage_progress = {
            WorkflowStage.PLANNING: 15,
            WorkflowStage.UIUX_DESIGN: 30,
            WorkflowStage.FRONTEND_DEV: 50,
            WorkflowStage.BACKEND_DEV: 70,
            WorkflowStage.DEVOPS_SETUP: 85,
            WorkflowStage.FILE_GENERATION: 95,
            WorkflowStage.PROJECT_DEPLOYMENT: 100,
            WorkflowStage.COMPLETED: 100,
            WorkflowStage.FAILED: 0
        }
    def _get_agents_for_model(self, model: str) -> Dict[str, Any]:
        """지정된 모델로 Agent들을 생성하거나 캐시에서 가져오기"""
        if model not in self.agents_cache:
            self.agents_cache[model] = {
                "pm": PMAgent(model=model),
                "uiux": UIUXAgent(model=model),
                "frontend": FrontendAgent(model=model),
                "backend": BackendAgent(model=model),
                "devops": DevOpsAgent(model=model)
            }
            logger.info(f"모델 {model}에 대한 Agent들을 생성했습니다.")
        
        return self.agents_cache[model]
    
    async def start_workflow(self, workflow_data: WorkflowCreateRequest) -> str:
        """새로운 워크플로 시작"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # 모델 선택 (기본값: settings.DEFAULT_GPT_MODEL)
            selected_model = workflow_data.model or settings.DEFAULT_GPT_MODEL
            
            # 선택된 모델이 사용 가능한지 확인
            if selected_model not in settings.AVAILABLE_MODELS:
                logger.warning(f"지원하지 않는 모델: {selected_model}, 기본 모델 사용: {settings.DEFAULT_GPT_MODEL}")
                selected_model = settings.DEFAULT_GPT_MODEL
            
            logger.info(f"워크플로 {workflow_id}에서 {selected_model} 모델 사용")
            
            # 워크플로 정보 초기화
            workflow_info = {
                "id": workflow_id,
                "user_input": workflow_data.user_input,
                "project_name": workflow_data.project_name,
                "model": selected_model,
                "status": WorkflowStatus.RUNNING,
                "created_at": datetime.now(),
                "current_stage": WorkflowStage.PLANNING,
                "stage_results": {},
                "progress_history": [],
                "error": None
            }
            
            self.active_workflows[workflow_id] = workflow_info
            
            # 워크플로 실행을 백그라운드 태스크로 시작
            asyncio.create_task(self._execute_workflow(workflow_id))
            
            logger.info(f"워크플로 시작: {workflow_id}")
            return workflow_id
            
        except Exception as e:
            logger.error(f"워크플로 시작 실패: {e}")
            raise Exception(f"워크플로 시작 실패: {str(e)}")
    
    async def _execute_workflow(self, workflow_id: str) -> None:
        """워크플로 실행"""
        try:
            workflow_info = self.active_workflows[workflow_id]
            logger.info(f"워크플로 실행 시작: {workflow_id}")
            
            # 단계별 실행
            stage_data = {
                "workflow_id": workflow_id,
                "user_input": workflow_info["user_input"],
                "project_name": workflow_info["project_name"]
            }
            
            logger.info(f"PM Agent 실행 준비: {stage_data}")
            
            # 선택된 모델에 대한 Agent들 가져오기
            agents = self._get_agents_for_model(workflow_info["model"])
            
            # 1. Planning (PM Agent)
            await self._update_progress(workflow_id, WorkflowStage.PLANNING, "프로젝트 계획 수립 중...")
            
            try:
                pm_result = await agents["pm"].safe_execute(stage_data)
                logger.info(f"PM Agent 실행 결과: {pm_result.get('success', False)}")
            except Exception as e:
                logger.error(f"PM Agent 실행 중 예외 발생: {e}")
                await self._handle_workflow_error(workflow_id, "PM Agent 실행 실패", str(e))
                return
            
            if not pm_result["success"]:
                await self._handle_workflow_error(workflow_id, "PM Agent 실행 실패", pm_result.get("error_message"))
                return
            
            workflow_info["stage_results"]["pm"] = pm_result["result"]
            stage_data.update(pm_result["result"])
            
            # 2. UI/UX Design
            await self._update_progress(workflow_id, WorkflowStage.UIUX_DESIGN, "UI/UX 설계 중...")
            
            try:
                uiux_result = await agents["uiux"].safe_execute(stage_data)
                logger.info(f"UI/UX Agent 실행 결과: {uiux_result.get('success', False)}")
            except Exception as e:
                logger.error(f"UI/UX Agent 실행 중 예외 발생: {e}")
                await self._handle_workflow_error(workflow_id, "UI/UX Agent 실행 실패", str(e))
                return
            
            if not uiux_result["success"]:
                await self._handle_workflow_error(workflow_id, "UI/UX Agent 실행 실패", uiux_result.get("error_message"))
                return
            
            workflow_info["stage_results"]["uiux"] = uiux_result["result"]
            stage_data.update(uiux_result["result"])
            
            # 3. Frontend Development
            await self._update_progress(workflow_id, WorkflowStage.FRONTEND_DEV, "프론트엔드 코드 생성 중...")
            
            try:
                frontend_result = await agents["frontend"].safe_execute(stage_data)
                logger.info(f"Frontend Agent 실행 결과: {frontend_result.get('success', False)}")
            except Exception as e:
                logger.error(f"Frontend Agent 실행 중 예외 발생: {e}")
                await self._handle_workflow_error(workflow_id, "Frontend Agent 실행 실패", str(e))
                return
            
            if not frontend_result["success"]:
                await self._handle_workflow_error(workflow_id, "Frontend Agent 실행 실패", frontend_result.get("error_message"))
                return
            
            workflow_info["stage_results"]["frontend"] = frontend_result["result"]
            stage_data.update(frontend_result["result"])
            
            # 4. Backend Development
            await self._update_progress(workflow_id, WorkflowStage.BACKEND_DEV, "백엔드 코드 생성 중...")
            
            try:
                backend_result = await agents["backend"].safe_execute(stage_data)
                logger.info(f"Backend Agent 실행 결과: {backend_result.get('success', False)}")
            except Exception as e:
                logger.error(f"Backend Agent 실행 중 예외 발생: {e}")
                await self._handle_workflow_error(workflow_id, "Backend Agent 실행 실패", str(e))
                return
            
            if not backend_result["success"]:
                await self._handle_workflow_error(workflow_id, "Backend Agent 실행 실패", backend_result.get("error_message"))
                return
            
            workflow_info["stage_results"]["backend"] = backend_result["result"]
            stage_data.update(backend_result["result"])
            
            # 5. DevOps Setup
            await self._update_progress(workflow_id, WorkflowStage.DEVOPS_SETUP, "DevOps 설정 생성 중...")
            
            try:
                devops_result = await agents["devops"].safe_execute(stage_data)
                logger.info(f"DevOps Agent 실행 결과: {devops_result.get('success', False)}")
            except Exception as e:
                logger.error(f"DevOps Agent 실행 중 예외 발생: {e}")
                await self._handle_workflow_error(workflow_id, "DevOps Agent 실행 실패", str(e))
                return
            
            if not devops_result["success"]:
                await self._handle_workflow_error(workflow_id, "DevOps Agent 실행 실패", devops_result.get("error_message"))
                return
            
            workflow_info["stage_results"]["devops"] = devops_result["result"]
            
            # 6. File Generation (MCP를 통한 실제 파일 생성)
            await self._update_progress(workflow_id, WorkflowStage.FILE_GENERATION, "프로젝트 파일 생성 중...")
            
            try:
                file_generation_result = await self._generate_project_files(workflow_id, workflow_info["stage_results"])
                logger.info(f"파일 생성 결과: {file_generation_result.get('success', False)}")
            except Exception as e:
                logger.error(f"파일 생성 중 예외 발생: {e}")
                await self._handle_workflow_error(workflow_id, "파일 생성 실패", str(e))
                return
            
            if not file_generation_result["success"]:
                await self._handle_workflow_error(workflow_id, "파일 생성 실패", file_generation_result.get("error"))
                return
            
            workflow_info["stage_results"]["file_generation"] = file_generation_result
            
            # 7. Project Deployment (선택적 자동 실행)
            await self._update_progress(workflow_id, WorkflowStage.PROJECT_DEPLOYMENT, "프로젝트 배포 준비 중...")
            
            try:
                deployment_result = await self._prepare_deployment(workflow_id, workflow_info["stage_results"])
                logger.info(f"배포 준비 결과: {deployment_result.get('success', False)}")
            except Exception as e:
                logger.error(f"배포 준비 중 예외 발생: {e}")
                # 배포 준비는 실패해도 워크플로를 중단하지 않음
                deployment_result = {"success": False, "error": str(e)}
            
            workflow_info["stage_results"]["deployment"] = deployment_result
            
            # 8. 완료
            await self._update_progress(workflow_id, WorkflowStage.COMPLETED, "프로젝트 생성 완료!")
            workflow_info["status"] = WorkflowStatus.COMPLETED
            workflow_info["completed_at"] = datetime.now()
            
            logger.info(f"워크플로 완료: {workflow_id}")
            
        except Exception as e:
            logger.error(f"워크플로 실행 중 치명적 오류: {e}")
            await self._handle_workflow_error(workflow_id, "워크플로 실행 오류", str(e))
    
    async def _update_progress(self, workflow_id: str, stage: WorkflowStage, message: str, 
                             stage_results: Optional[Dict[str, Any]] = None) -> None:
        """진행상황 업데이트"""
        try:
            workflow_info = self.active_workflows.get(workflow_id)
            if not workflow_info:
                return
            
            progress = WorkflowProgress(
                workflow_id=workflow_id,
                stage=stage,
                progress_percentage=self.stage_progress[stage],
                current_agent=stage.value,
                message=message,
                timestamp=datetime.now(),
                stage_results=stage_results
            )
            
            workflow_info["current_stage"] = stage
            workflow_info["progress_history"].append(asdict(progress))
            
            logger.info(f"워크플로 진행: {workflow_id} - {stage.value} ({self.stage_progress[stage]}%)")
            
        except Exception as e:
            logger.error(f"진행상황 업데이트 실패: {e}")
    
    async def _handle_workflow_error(self, workflow_id: str, error_type: str, error_message: str) -> None:
        """워크플로 오류 처리"""
        try:
            workflow_info = self.active_workflows.get(workflow_id)
            if not workflow_info:
                return
            
            workflow_info["status"] = WorkflowStatus.FAILED
            workflow_info["error"] = {
                "type": error_type,
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            }
            
            await self._update_progress(
                workflow_id, 
                WorkflowStage.FAILED, 
                f"오류 발생: {error_message}",
                {"error": error_message}
            )
            
            logger.error(f"워크플로 실패: {workflow_id} - {error_type}: {error_message}")
            
        except Exception as e:
            logger.error(f"오류 처리 실패: {e}")
    
    async def _generate_project_files(self, workflow_id: str, stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """MCP를 통한 실제 프로젝트 파일 생성"""
        try:
            project_plan = stage_results.get("pm", {}).get("project_plan", {})
            project_name = project_plan.get("project_name", "web-app")
            
            # 프로젝트 디렉토리 경로
            project_path = f"{settings.WORKSPACE_DIR}/generated_projects/{project_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            # 모든 파일 수집
            all_files = {}
            
            # Frontend 파일
            frontend_files = stage_results.get("frontend", {}).get("files", {})
            for file_path, content in frontend_files.items():
                all_files[f"frontend/{file_path}"] = content
            
            # Backend 파일
            backend_files = stage_results.get("backend", {}).get("files", {})
            for file_path, content in backend_files.items():
                all_files[f"backend/{file_path}"] = content
            
            # DevOps 파일
            devops_files = stage_results.get("devops", {}).get("devops_files", {})
            for file_path, content in devops_files.items():
                all_files[file_path] = content
            
            # MCP 매니저를 통한 파일 생성
            project_data = {
                "project_name": project_name,
                "file_structure": all_files,
                "environment": {
                    "development": {
                        "NODE_ENV": "development",
                        "API_URL": "http://localhost:8000"
                    }
                }
            }
            
            result = await self.mcp_manager.create_complete_project(project_data)
            
            if not result["success"]:
                raise Exception(result.get("error", "프로젝트 생성 실패"))
            
            return {
                "success": True,
                "project_path": result["project_path"],
                "files_created": len(result["files_created"]),
                "project_name": project_name
            }
            
        except Exception as e:
            logger.error(f"파일 생성 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _prepare_deployment(self, workflow_id: str, stage_results: Dict[str, Any]) -> Dict[str, Any]:
        """배포 준비"""
        try:
            file_generation = stage_results.get("file_generation", {})
            project_path = file_generation.get("project_path")
            
            if not project_path:
                return {"success": False, "error": "프로젝트 경로를 찾을 수 없습니다."}
            
            devops_config = stage_results.get("devops", {}).get("deployment_config", {})
            
            # 환경변수 파일 생성 (MCP manager에서 이미 처리됨)
            # deployment는 별도 설정으로 관리
            
            return {
                "success": True,
                "project_path": project_path,
                "deployment_config": devops_config,
                "ready_for_deployment": True,
                "instructions": {
                    "manual_start": f"cd {project_path} && ./run.sh",
                    "frontend_url": devops_config.get("frontend_url"),
                    "backend_url": devops_config.get("backend_url"),
                    "api_docs_url": f"{devops_config.get('backend_url')}/docs"
                }
            }
            
        except Exception as e:
            logger.error(f"배포 준비 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """워크플로 상태 조회"""
        workflow_info = self.active_workflows.get(workflow_id)
        if not workflow_info:
            return None
        
        return {
            "id": workflow_info["id"],
            "status": workflow_info["status"],
            "current_stage": workflow_info["current_stage"].value if workflow_info["current_stage"] else None,
            "progress_percentage": self.stage_progress.get(workflow_info["current_stage"], 0),
            "created_at": workflow_info["created_at"].isoformat(),
            "completed_at": workflow_info.get("completed_at").isoformat() if workflow_info.get("completed_at") else None,
            "error": workflow_info.get("error"),
            "project_name": workflow_info.get("project_name"),
            "latest_progress": workflow_info["progress_history"][-1] if workflow_info["progress_history"] else None
        }
    
    async def get_workflow_progress_stream(self, workflow_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """워크플로 진행상황 스트림"""
        last_progress_count = 0
        
        while True:
            workflow_info = self.active_workflows.get(workflow_id)
            if not workflow_info:
                break
            
            # 새로운 진행상황만 전송
            progress_history = workflow_info["progress_history"]
            if len(progress_history) > last_progress_count:
                for progress in progress_history[last_progress_count:]:
                    yield progress
                last_progress_count = len(progress_history)
            
            # 워크플로가 완료되거나 실패하면 스트림 종료
            if workflow_info["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break
            
            await asyncio.sleep(1)  # 1초마다 체크
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """활성 워크플로 목록"""
        return [
            {
                "id": workflow_id,
                "status": info["status"],
                "current_stage": info["current_stage"].value if info["current_stage"] else None,
                "progress_percentage": self.stage_progress.get(info["current_stage"], 0),
                "created_at": info["created_at"].isoformat(),
                "project_name": info.get("project_name")
            }
            for workflow_id, info in self.active_workflows.items()
        ]
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """워크플로 취소"""
        try:
            workflow_info = self.active_workflows.get(workflow_id)
            if not workflow_info:
                return False
            
            workflow_info["status"] = WorkflowStatus.CANCELLED
            await self._update_progress(workflow_id, WorkflowStage.FAILED, "워크플로가 취소되었습니다.")
            
            logger.info(f"워크플로 취소: {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"워크플로 취소 실패: {e}")
            return False
    
    async def cleanup_completed_workflows(self, max_age_hours: int = 24) -> int:
        """완료된 워크플로 정리"""
        try:
            cleaned_count = 0
            current_time = datetime.now()
            
            for workflow_id, info in list(self.active_workflows.items()):
                if info["status"] in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                    age = current_time - info["created_at"]
                    if age.total_seconds() > max_age_hours * 3600:
                        del self.active_workflows[workflow_id]
                        cleaned_count += 1
            
            logger.info(f"워크플로 정리 완료: {cleaned_count}개 정리됨")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"워크플로 정리 실패: {e}")
            return 0
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """워크플로 통계"""
        try:
            total_workflows = len(self.active_workflows)
            status_counts = {}
            
            for info in self.active_workflows.values():
                status = info["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "total_workflows": total_workflows,
                "status_breakdown": status_counts,
                "active_agents": ["pm", "uiux", "frontend", "backend", "devops"],
                "average_completion_time": self._calculate_average_completion_time()
            }
            
        except Exception as e:
            logger.error(f"통계 생성 실패: {e}")
            return {"error": str(e)}
    
    def _calculate_average_completion_time(self) -> Optional[float]:
        """평균 완료 시간 계산"""
        try:
            completed_workflows = [
                info for info in self.active_workflows.values()
                if info["status"] == WorkflowStatus.COMPLETED and info.get("completed_at")
            ]
            
            if not completed_workflows:
                return None
            
            total_time = sum(
                (info["completed_at"] - info["created_at"]).total_seconds()
                for info in completed_workflows
            )
            
            return total_time / len(completed_workflows)
            
        except Exception:
            return None


# 전역 워크플로 매니저 인스턴스
workflow_manager = WorkflowManager()
