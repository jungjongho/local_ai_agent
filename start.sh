#!/bin/bash

# 멀티 AI 에이전트 웹서비스 생성 시스템 시작 스크립트

echo "🚀 멀티 AI 에이전트 웹서비스 생성 시스템 시작"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
check_requirements() {
    echo -e "${BLUE}📋 시스템 요구사항 확인 중...${NC}"
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3가 설치되어 있지 않습니다.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Python3: $(python3 --version)${NC}"
    
    # Node.js 확인
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js가 설치되어 있지 않습니다.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Node.js: $(node --version)${NC}"
    
    # npm 확인
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm이 설치되어 있지 않습니다.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ npm: $(npm --version)${NC}"
    
    echo -e "${GREEN}✅ 모든 요구사항이 만족되었습니다.${NC}"
}

setup_environment() {
    echo -e "${BLUE}🔧 환경 설정 중...${NC}"
    
    # .env 파일 확인 및 생성
    if [ ! -f backend/.env ]; then
        echo -e "${YELLOW}⚠️  .env 파일이 없습니다. .env.example에서 복사합니다.${NC}"
        cp backend/.env.example backend/.env
        echo -e "${YELLOW}⚠️  backend/.env 파일을 수정하여 API 키를 설정하세요.${NC}"
    fi
    
    # workspace 디렉토리 생성
    mkdir -p workspace/generated_projects
    echo -e "${GREEN}✅ 작업 공간 디렉토리 생성 완료${NC}"
}

install_dependencies() {
    echo -e "${BLUE}📦 의존성 설치 중...${NC}"
    
    # Backend 의존성 설치
    echo -e "${BLUE}📦 Backend 의존성 설치 중...${NC}"
    cd backend
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}🐍 Python 가상환경 생성 중...${NC}"
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend 의존성 설치
    echo -e "${BLUE}📦 Frontend 의존성 설치 중...${NC}"
    cd frontend
    npm install
    cd ..
    
    echo -e "${GREEN}✅ 모든 의존성 설치 완료${NC}"
}

start_services() {
    echo -e "${BLUE}🚀 서비스 시작 중...${NC}"
    
    # Backend 시작 (백그라운드)
    echo -e "${BLUE}🔧 Backend 서버 시작 중... (포트 8000)${NC}"
    cd backend
    source venv/bin/activate
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # 잠시 대기
    sleep 3
    
    # Frontend 시작 (백그라운드)
    echo -e "${BLUE}⚛️  Frontend 서버 시작 중... (포트 3000)${NC}"
    cd frontend
    nohup npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # PID 저장
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo -e "${GREEN}✅ 서비스 시작 완료!${NC}"
    echo ""
    echo -e "${GREEN}🌐 Frontend: http://localhost:3000${NC}"
    echo -e "${GREEN}🔧 Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}📚 API 문서: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}❤️  헬스 체크: http://localhost:8000/health${NC}"
    echo ""
    echo -e "${YELLOW}💡 서비스를 중지하려면 ./stop.sh를 실행하세요.${NC}"
    echo -e "${YELLOW}📊 로그를 보려면 tail -f logs/backend.log 또는 tail -f logs/frontend.log를 실행하세요.${NC}"
}

# 메인 실행
main() {
    # 로그 디렉토리 생성
    mkdir -p logs
    
    check_requirements
    setup_environment
    install_dependencies
    start_services
}

# 스크립트 실행
main

echo -e "${GREEN}🎉 멀티 AI 에이전트 웹서비스 생성 시스템이 성공적으로 시작되었습니다!${NC}"
