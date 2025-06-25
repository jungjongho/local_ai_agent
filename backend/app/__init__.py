"""
멀티 AI 에이전트 웹서비스 생성 시스템 - Backend Application

이 패키지는 사용자 입력으로부터 완전한 웹서비스를 자동 생성하는
AI 에이전트 시스템의 백엔드 애플리케이션입니다.

주요 구성요소:
- FastAPI 기반 웹 API 서버
- 5개의 전문화된 AI 에이전트 (PM, UI/UX, Frontend, Backend, DevOps)
- MCP(Model Context Protocol)를 통한 파일 시스템 접근
- 실시간 워크플로 모니터링
- SQLite 기반 데이터 저장
"""

__version__ = "1.0.0"
__author__ = "AI Agent Development Team"
__description__ = "멀티 AI 에이전트 웹서비스 생성 시스템"

# 패키지 초기화 로깅
import logging
logger = logging.getLogger(__name__)
logger.info(f"🚀 {__description__} v{__version__} 패키지 로드됨")

# 주요 구성요소 import (선택적으로 로드)
try:
    from .core.config import settings
    logger.info("✅ 설정 모듈 로드 완료")
except ImportError as e:
    logger.warning(f"⚠️ 설정 모듈 로드 실패: {e}")
    settings = None

try:
    from .workflow_manager import WorkflowManager
    logger.info("✅ 워크플로 매니저 로드 완료")
except ImportError as e:
    logger.warning(f"⚠️ 워크플로 매니저 로드 실패: {e}")
    WorkflowManager = None

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "settings",
    "WorkflowManager"
]
