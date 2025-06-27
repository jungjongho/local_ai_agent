#!/bin/bash

# 디버깅 스크립트 - 시스템 상태 확인

echo "🔍 AI Agent System 디버깅 도구"
echo "==============================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. 포트 상태 확인${NC}"
echo "Frontend 포트 (3000):"
lsof -i :3000 || echo "포트 3000: 사용되지 않음"

echo ""
echo "Backend 포트 (8000):"
lsof -i :8000 || echo "포트 8000: 사용되지 않음"

echo ""
echo -e "${BLUE}2. Python 가상환경 확인${NC}"
cd backend
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Python 가상환경 존재${NC}"
    source venv/bin/activate
    echo "Python 버전: $(python --version)"
    echo "OpenAI 패키지: $(pip show openai | grep Version || echo '설치되지 않음')"
    deactivate
else
    echo -e "${RED}❌ Python 가상환경 없음${NC}"
fi
cd ..

echo ""
echo -e "${BLUE}3. Node.js 환경 확인${NC}"
cd frontend
if [ -d "node_modules" ]; then
    echo -e "${GREEN}✅ Node.js 모듈 설치됨${NC}"
else
    echo -e "${RED}❌ Node.js 모듈 설치 필요${NC}"
fi
echo "Node.js 버전: $(node --version)"
echo "npm 버전: $(npm --version)"
cd ..

echo ""
echo -e "${BLUE}4. API 연결 테스트${NC}"
echo "Backend 헬스 체크:"
curl -s http://localhost:8000/health || echo -e "${RED}❌ Backend 서버 응답 없음${NC}"

echo ""
echo "API 상태 체크:"
curl -s http://localhost:8000/api/v1/status || echo -e "${RED}❌ API 서버 응답 없음${NC}"

echo ""
echo -e "${BLUE}5. 환경변수 확인${NC}"
cd backend
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env 파일 존재${NC}"
    echo "OPENAI_API_KEY 설정: $(grep -q "OPENAI_API_KEY=sk-" .env && echo "✅ 설정됨" || echo "❌ 설정 안됨")"
    echo "PORT 설정: $(grep "PORT=" .env)"
else
    echo -e "${RED}❌ .env 파일 없음${NC}"
fi
cd ..

echo ""
echo -e "${BLUE}6. 로그 파일 확인${NC}"
if [ -d "logs" ]; then
    echo "로그 디렉토리 존재: ✅"
    ls -la logs/
else
    echo "로그 디렉토리 없음: ❌"
fi

echo ""
echo -e "${YELLOW}💡 문제 해결 방법:${NC}"
echo "1. Backend 서버가 응답하지 않으면:"
echo "   cd backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "2. Frontend 서버 시작:"
echo "   cd frontend && npm run dev"
echo ""
echo "3. 전체 시스템 재시작:"
echo "   ./stop.sh && ./start.sh"
