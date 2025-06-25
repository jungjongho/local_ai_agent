from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API 설정
    OPENAI_API_KEY: Optional[str] = None
    API_V1_STR: str = "/api/v1"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8025
    
    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./local_ai_agent.db"
    
    # 프로젝트 경로
    WORKSPACE_PATH: str = "../workspace/generated_projects"
    WORKSPACE_DIR: str = "../workspace/generated_projects"
    TEMPLATES_PATH: str = "./templates"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3025", "http://localhost:3000"]
    CORS_ORIGINS: List[str] = ["http://localhost:3025", "http://localhost:3000"]
    
    # WebSocket 설정
    WS_HOST: str = "localhost"
    WS_PORT: int = 8001
    
    # 로깅
    LOG_LEVEL: str = "INFO"
    
    @property
    def workspace_absolute_path(self) -> Path:
        """워크스페이스 절대 경로 반환"""
        current_dir = Path(__file__).parent.parent
        return (current_dir / self.WORKSPACE_PATH).resolve()
    
    @property
    def templates_absolute_path(self) -> Path:
        """템플릿 절대 경로 반환"""
        current_dir = Path(__file__).parent.parent
        return (current_dir / self.TEMPLATES_PATH).resolve()
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 전역 설정 인스턴스
settings = Settings()
