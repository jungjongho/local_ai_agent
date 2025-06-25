#!/bin/bash

# 빠른 테스트 및 디버깅 스크립트

echo "🔍 멀티 AI 에이전트 시스템 - 빠른 진단 및 테스트"
echo "=================================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 시스템 요구사항 확인
echo -e "${BLUE}📋 1. 시스템 요구사항 확인${NC}"
echo "Python 버전: $(python3 --version 2>/dev/null || echo '❌ Python3 미설치')"
echo "Node.js 버전: $(node --version 2>/dev/null || echo '❌ Node.js 미설치')"
echo "npm 버전: $(npm --version 2>/dev/null || echo '❌ npm 미설치')"
echo ""

# 2. 포트 사용 현황 확인
echo -e "${BLUE}📋 2. 포트 사용 현황 확인${NC}"
echo "포트 3000 사용 현황:"
lsof -i :3000 | head -5 || echo "포트 3000 사용 안함"
echo "포트 8000 사용 현황:"
lsof -i :8000 | head -5 || echo "포트 8000 사용 안함"
echo ""

# 3. Backend 테스트 모드 실행
echo -e "${BLUE}📋 3. Backend 테스트 모드 실행${NC}"
echo "테스트용 백엔드 서버를 시작합니다..."

cd backend

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "🐍 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 기본 의존성만 설치
echo "📦 기본 의존성 설치 중..."
pip install fastapi uvicorn python-multipart python-dotenv

# 환경변수 파일 생성
if [ ! -f ".env" ]; then
    echo "🔧 .env 파일 생성 중..."
    cat > .env << EOF
ENVIRONMENT=test
DEBUG=true
OPENAI_API_KEY=test-key-not-required-for-basic-test
CORS_ORIGINS=["http://localhost:3000"]
EOF
fi

echo "🚀 테스트 백엔드 서버 시작 중..."
echo "📍 Backend: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs" 
echo "⏹️ 중지하려면 Ctrl+C를 누르세요"
echo ""

# 백그라운드에서 테스트 서버 실행
nohup python test_main.py > ../logs/test_backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../test_backend.pid

# 서버 시작 대기
echo "⏳ 서버 시작 대기 중..."
sleep 3

# 헬스 체크
echo "🔍 백엔드 헬스 체크..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ 백엔드 서버 정상 동작${NC}"
else
    echo -e "${RED}❌ 백엔드 서버 응답 없음${NC}"
fi

cd ..

# 4. Frontend 테스트
echo -e "${BLUE}📋 4. Frontend 테스트${NC}"
cd frontend

# node_modules 확인
if [ ! -d "node_modules" ]; then
    echo "📦 Frontend 의존성 설치 중..."
    npm install
fi

echo "🚀 Frontend 개발 서버 시작 중..."
echo "📍 Frontend: http://localhost:3000"
echo "🔗 테스트 페이지: http://localhost:3000/test"
echo "⏹️ 중지하려면 Ctrl+C를 누르세요"
echo ""

# 백그라운드에서 프론트엔드 실행
nohup npm run dev > ../logs/test_frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../test_frontend.pid

cd ..

# 서버 시작 대기
echo "⏳ Frontend 서버 시작 대기 중..."
sleep 5

# 상태 확인
echo -e "${BLUE}📋 5. 전체 시스템 상태 확인${NC}"
echo "PID 파일:"
ls -la *.pid 2>/dev/null || echo "PID 파일 없음"

echo ""
echo "로그 파일:"
ls -la logs/ 2>/dev/null || echo "로그 파일 없음"

echo ""
echo "프로세스 확인:"
ps aux | grep -E "(test_main|vite)" | grep -v grep || echo "관련 프로세스 없음"

echo ""
echo -e "${GREEN}🎉 테스트 시스템 시작 완료!${NC}"
echo ""
echo "📋 접속 정보:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend: http://localhost:8000"
echo "  • API 문서: http://localhost:8000/docs"
echo "  • 테스트 페이지: http://localhost:3000/test"
echo ""
echo "📊 로그 확인:"
echo "  • Backend: tail -f logs/test_backend.log"
echo "  • Frontend: tail -f logs/test_frontend.log"
echo ""
echo "🛑 중지 방법:"
echo "  • ./test_stop.sh 실행"
echo "  • 또는 kill \$(cat test_backend.pid) && kill \$(cat test_frontend.pid)"
