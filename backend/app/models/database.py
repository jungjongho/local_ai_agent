from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional, AsyncGenerator
import asyncio
import os
from ..core.config import settings

Base = declarative_base()

# 데이터베이스 설정
DATABASE_URL = settings.DATABASE_URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class WorkflowModel(Base):
    """워크플로 모델"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    user_input = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    current_agent = Column(String(100), nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    
    # 결과 데이터
    planning_result = Column(JSON, nullable=True)
    uiux_result = Column(JSON, nullable=True)
    frontend_result = Column(JSON, nullable=True)
    backend_result = Column(JSON, nullable=True)
    devops_result = Column(JSON, nullable=True)
    
    # 생성된 파일 경로
    project_path = Column(String(500), nullable=True)
    
    # 타임스탬프
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # 오류 정보
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환"""
        return {
            "id": self.id,
            "project_name": self.project_name,
            "user_input": self.user_input,
            "status": self.status,
            "current_agent": self.current_agent,
            "progress": self.progress,
            "planning_result": self.planning_result,
            "uiux_result": self.uiux_result,
            "frontend_result": self.frontend_result,
            "backend_result": self.backend_result,
            "devops_result": self.devops_result,
            "project_path": self.project_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
        }


class AgentLogModel(Base):
    """에이전트 실행 로그 모델"""
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=False)
    agent_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)  # started, completed, failed
    
    # 입력/출력 데이터
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    error_data = Column(JSON, nullable=True)
    
    # 성능 메트릭
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # GPT 사용량
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(String(20), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """모델을 딕셔너리로 변환"""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "agent_name": self.agent_name,
            "status": self.status,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_data": self.error_data,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration_seconds,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
        }


# 데이터베이스 유틸리티 함수들
from datetime import timedelta

async def init_db():
    """데이터베이스 초기화"""
    try:
        # 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✅ 데이터베이스 초기화 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        raise


def get_db_session() -> Session:
    """데이터베이스 세션 생성"""
    return SessionLocal()


async def get_db_session_async() -> AsyncGenerator[Session, None]:
    """비동기 데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_workflow(db: Session, workflow_data: Dict[str, Any]) -> WorkflowModel:
    """워크플로 생성"""
    workflow = WorkflowModel(
        project_name=workflow_data["project_name"],
        user_input=workflow_data["user_input"],
        status="pending"
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    return workflow


def get_workflow(db: Session, workflow_id: int) -> Optional[WorkflowModel]:
    """워크플로 조회"""
    return db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()


def update_workflow(db: Session, workflow_id: int, update_data: Dict[str, Any]) -> Optional[WorkflowModel]:
    """워크플로 업데이트"""
    workflow = db.query(WorkflowModel).filter(WorkflowModel.id == workflow_id).first()
    if workflow:
        for key, value in update_data.items():
            if hasattr(workflow, key):
                setattr(workflow, key, value)
        workflow.updated_at = datetime.now()
        db.commit()
        db.refresh(workflow)
    return workflow


def list_workflows(db: Session, limit: int = 100, offset: int = 0) -> list[WorkflowModel]:
    """워크플로 목록 조회"""
    return db.query(WorkflowModel).order_by(WorkflowModel.created_at.desc()).offset(offset).limit(limit).all()


def create_agent_log(db: Session, log_data: Dict[str, Any]) -> AgentLogModel:
    """에이전트 로그 생성"""
    log = AgentLogModel(
        workflow_id=log_data["workflow_id"],
        agent_name=log_data["agent_name"],
        status=log_data["status"],
        input_data=log_data.get("input_data"),
        output_data=log_data.get("output_data"),
        error_data=log_data.get("error_data"),
        tokens_used=log_data.get("tokens_used", 0),
        cost_usd=log_data.get("cost_usd")
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_agent_log(db: Session, log_id: int, update_data: Dict[str, Any]) -> Optional[AgentLogModel]:
    """에이전트 로그 업데이트"""
    log = db.query(AgentLogModel).filter(AgentLogModel.id == log_id).first()
    if log:
        for key, value in update_data.items():
            if hasattr(log, key):
                setattr(log, key, value)
        if "end_time" in update_data and log.start_time:
            # 지속 시간 계산
            duration = (update_data["end_time"] - log.start_time).total_seconds()
            log.duration_seconds = int(duration)
        db.commit()
        db.refresh(log)
    return log


def get_workflow_logs(db: Session, workflow_id: int) -> list[AgentLogModel]:
    """워크플로의 에이전트 로그 조회"""
    return db.query(AgentLogModel).filter(AgentLogModel.workflow_id == workflow_id).order_by(AgentLogModel.start_time).all()


def cleanup_old_workflows(db: Session, days_old: int = 30) -> int:
    """오래된 워크플로 정리"""
    cutoff_date = datetime.now() - timedelta(days=days_old)
    
    # 오래된 워크플로 조회
    old_workflows = db.query(WorkflowModel).filter(
        WorkflowModel.created_at < cutoff_date,
        WorkflowModel.status.in_(["completed", "failed"])
    ).all()
    
    count = len(old_workflows)
    
    # 관련 로그 먼저 삭제
    for workflow in old_workflows:
        db.query(AgentLogModel).filter(AgentLogModel.workflow_id == workflow.id).delete()
    
    # 워크플로 삭제
    for workflow in old_workflows:
        db.delete(workflow)
    
    db.commit()
    return count
