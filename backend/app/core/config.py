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
    
    # GPT 모델 설정
    DEFAULT_GPT_MODEL: str = "gpt-4o-mini"
    AVAILABLE_MODELS: List[str] = [
        "gpt-4.1",             # Latest flagship model (2025, 최고급)
        "gpt-4.1-mini",        # Latest efficient model (2025, 빠름)
        "gpt-4.1-nano",        # Latest nano model (2025, 가장 빠름)
        "gpt-4o",              # Multimodal model (멀티모달)
        "gpt-4o-mini",         # Cost-efficient model (저렴)
        "gpt-4-turbo",         # Previous flagship (안정적)
        "gpt-4",               # Standard GPT-4 (표준)
        "gpt-3.5-turbo",       # Most affordable (가장 저렴)
    ]
    
    # 모델별 설명
    MODEL_DESCRIPTIONS: dict = {
        "gpt-4.1": "최신 플래그십 모델 (2025) - 코딩과 복합 추론에 최적, 1M 토큰 컨텍스트",
        "gpt-4.1-mini": "최신 효율적 모델 (2025) - 빠르고 저렴하면서도 고성능",
        "gpt-4.1-nano": "최신 나노 모델 (2025) - 가장 빠르고 경제적인 모델",
        "gpt-4o": "멀티모달 모델 - 텍스트, 이미지, 오디오 처리 가능",
        "gpt-4o-mini": "비용 효율적인 소형 모델 - 일반적인 작업에 최적",
        "gpt-4-turbo": "이전 플래그십 모델 - 안정적이고 검증된 성능",
        "gpt-4": "표준 GPT-4 모델 - 범용적 사용",
        "gpt-3.5-turbo": "가장 저렴한 모델 - 간단한 작업에 적합"
    }
    
    # 모델별 추천 사용 케이스
    MODEL_USE_CASES: dict = {
        "gpt-4.1": ["복잡한 코딩", "고급 추론", "대용량 문서 처리"],
        "gpt-4.1-mini": ["일반적인 웹앱 생성", "빠른 프로토타이핑"],
        "gpt-4.1-nano": ["간단한 앱", "실시간 처리"],
        "gpt-4o": ["이미지 포함 앱", "멀티미디어 처리"],
        "gpt-4o-mini": ["기본 웹앱", "CRUD 애플리케이션"],
        "gpt-4-turbo": ["안정성 우선", "검증된 워크플로"],
        "gpt-4": ["범용 애플리케이션"],
        "gpt-3.5-turbo": ["간단한 할일 앱", "기본 기능만"]
    }
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 데이터베이스
    DATABASE_URL: str = "sqlite:///./local_ai_agent.db"
    
    # 프로젝트 경로
    WORKSPACE_PATH: str = "../workspace/generated_projects"
    WORKSPACE_DIR: str = "../workspace/generated_projects"
    TEMPLATES_PATH: str = "./templates"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
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
