#!/usr/bin/env python3
"""
Local AI Agent 서버 실행 스크립트
프로젝트 루트에서 실행하여 모듈 경로 문제를 해결합니다.
"""
import sys
import uvicorn
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 이제 backend 모듈을 정상적으로 import 가능
from backend.config.settings import settings

if __name__ == "__main__":
    print(f"🚀 Local AI Agent 서버를 시작합니다...")
    print(f"📂 프로젝트 루트: {PROJECT_ROOT}")
    print(f"🌐 서버 주소: http://{settings.api_host}:{settings.api_port}")
    print(f"📚 API 문서: http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "backend.main:app",  # 모듈 경로 수정
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )
