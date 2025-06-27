#!/bin/bash

# 실시간 로그 모니터링 스크립트

echo "🔍 AI Agent System 실시간 로그 모니터링"
echo "========================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 디렉토리 생성
mkdir -p logs

# 현재 실행 중인 프로세스 확인
echo -e "${BLUE}현재 실행 중인 프로세스:${NC}"
ps aux | grep -E "(uvicorn|node|npm)" | grep -v grep

echo ""
echo -e "${BLUE}포트 사용 상태:${NC}"
echo "포트 3000 (Frontend):"
lsof -i :3000 2>/dev/null || echo "사용되지 않음"
echo "포트 8000 (Backend):"
lsof -i :8000 2>/dev/null || echo "사용되지 않음"

echo ""
echo -e "${YELLOW}백엔드 수동 시작 (디버깅 모드):${NC}"
echo "================================"

cd backend

# Python 가상환경 활성화
if [ -d "venv" ]; then
    echo "Python 가상환경 활성화 중..."
    source venv/bin/activate
    
    # OpenAI 패키지 확인
    echo "OpenAI 패키지 상태:"
    pip show openai || echo "OpenAI 패키지가 설치되지 않음"
    
    # 환경변수 확인
    echo ""
    echo "환경변수 확인:"
    if [ -f ".env" ]; then
        echo "✅ .env 파일 존재"
        echo "OPENAI_API_KEY: $(grep "OPENAI_API_KEY=" .env | cut -d'=' -f2 | cut -c1-20)..."
        echo "PORT: $(grep "PORT=" .env)"
    else
        echo "❌ .env 파일 없음"
    fi
    
    echo ""
    echo -e "${GREEN}백엔드 서버 시작 (상세 로그 모드):${NC}"
    echo "Ctrl+C로 중지할 수 있습니다."
    echo "----------------------------------------"
    
    # 백엔드 서버를 상세 로그와 함께 시작
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug 2>&1 | tee ../logs/backend_debug.log
    
else
    echo "❌ Python 가상환경이 없습니다."
    echo "다음 명령어로 설정하세요:"
    echo "python3 -m venv venv"
    echo "source venv/bin/activate"
    echo "pip install -r requirements.txt"
fi
