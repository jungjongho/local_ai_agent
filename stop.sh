#!/bin/bash

# 멀티 AI 에이전트 웹서비스 생성 시스템 중지 스크립트

echo "🛑 멀티 AI 에이전트 웹서비스 생성 시스템 중지"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Backend 프로세스 중지
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo -e "${BLUE}🔧 Backend 서버 중지 중... (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID
        echo -e "${GREEN}✅ Backend 서버 중지 완료${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend 서버가 이미 중지되어 있습니다.${NC}"
    fi
    rm .backend.pid
else
    echo -e "${YELLOW}⚠️  Backend PID 파일을 찾을 수 없습니다.${NC}"
fi

# Frontend 프로세스 중지
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo -e "${BLUE}⚛️  Frontend 서버 중지 중... (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ Frontend 서버 중지 완료${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend 서버가 이미 중지되어 있습니다.${NC}"
    fi
    rm .frontend.pid
else
    echo -e "${YELLOW}⚠️  Frontend PID 파일을 찾을 수 없습니다.${NC}"
fi

# 포트 기반으로 남은 프로세스 정리
echo -e "${BLUE}🧹 포트 기반 프로세스 정리 중...${NC}"

# 포트 8000 (Backend)
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo -e "${BLUE}🔧 포트 8000의 프로세스 중지 중... (PID: $BACKEND_PORT_PID)${NC}"
    kill -9 $BACKEND_PORT_PID 2>/dev/null
fi

# 포트 3000 (Frontend)
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo -e "${BLUE}⚛️  포트 3000의 프로세스 중지 중... (PID: $FRONTEND_PORT_PID)${NC}"
    kill -9 $FRONTEND_PORT_PID 2>/dev/null
fi

echo -e "${GREEN}✅ 모든 서비스가 중지되었습니다.${NC}"
echo -e "${BLUE}💡 다시 시작하려면 ./start.sh를 실행하세요.${NC}"
