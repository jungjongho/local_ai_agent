#!/bin/bash

# 테스트 시스템 중지 스크립트

echo "🛑 테스트 시스템 중지 중..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# PID 파일들 확인 및 프로세스 종료
if [ -f "test_backend.pid" ]; then
    BACKEND_PID=$(cat test_backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${YELLOW}🔧 Backend 프로세스 종료 중... (PID: $BACKEND_PID)${NC}"
        kill $BACKEND_PID
        sleep 2
        if kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${RED}강제 종료...${NC}"
            kill -9 $BACKEND_PID
        fi
        echo -e "${GREEN}✅ Backend 종료 완료${NC}"
    else
        echo -e "${YELLOW}⚠️ Backend 프로세스가 이미 종료됨${NC}"
    fi
    rm -f test_backend.pid
fi

if [ -f "test_frontend.pid" ]; then
    FRONTEND_PID=$(cat test_frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}⚛️ Frontend 프로세스 종료 중... (PID: $FRONTEND_PID)${NC}"
        kill $FRONTEND_PID
        sleep 2
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            echo -e "${RED}강제 종료...${NC}"
            kill -9 $FRONTEND_PID
        fi
        echo -e "${GREEN}✅ Frontend 종료 완료${NC}"
    else
        echo -e "${YELLOW}⚠️ Frontend 프로세스가 이미 종료됨${NC}"
    fi
    rm -f test_frontend.pid
fi

# 추가로 포트 사용 프로세스 확인 및 정리
echo -e "${YELLOW}🔍 포트 사용 프로세스 확인 중...${NC}"

# 포트 3000 정리
PORT_3000_PID=$(lsof -ti:3000)
if [ ! -z "$PORT_3000_PID" ]; then
    echo -e "${YELLOW}포트 3000 사용 프로세스 종료: $PORT_3000_PID${NC}"
    kill $PORT_3000_PID 2>/dev/null
fi

# 포트 8000 정리  
PORT_8000_PID=$(lsof -ti:8000)
if [ ! -z "$PORT_8000_PID" ]; then
    echo -e "${YELLOW}포트 8000 사용 프로세스 종료: $PORT_8000_PID${NC}"
    kill $PORT_8000_PID 2>/dev/null
fi

echo -e "${GREEN}🎉 모든 테스트 프로세스가 종료되었습니다.${NC}"
echo ""
echo "📊 정리된 내용:"
echo "  • Backend 프로세스 종료"
echo "  • Frontend 프로세스 종료"  
echo "  • PID 파일 삭제"
echo "  • 포트 3000, 8000 해제"
echo ""
echo "💡 다시 시작하려면: ./test_start.sh"
