#!/bin/bash

# 개발용 간단 실행 스크립트 - Backend Only

echo "🔧 Backend 개발 서버 시작"

# 현재 디렉토리 확인
if [ ! -f "requirements.txt" ]; then
    echo "❌ backend 디렉토리에서 실행해주세요."
    echo "실행 방법: cd backend && ./dev.sh"
    exit 1
fi

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "🐍 Python 가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo "📦 의존성을 확인합니다..."
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️ .env 파일이 없습니다. .env.example을 복사합니다..."
    cp .env.example .env
    echo "🔑 .env 파일에서 OPENAI_API_KEY를 설정하세요."
fi

# 워크스페이스 디렉토리 생성
mkdir -p ../workspace/generated_projects

echo "🚀 FastAPI 서버를 시작합니다..."
echo "📍 Backend: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo "❤️ 헬스 체크: http://localhost:8000/health"
echo "⏹️ 중지하려면 Ctrl+C를 누르세요"
echo ""

# 서버 실행 (app 모듈로 실행)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
