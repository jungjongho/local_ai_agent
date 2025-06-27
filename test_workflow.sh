#!/bin/bash

# 워크플로 생성 시 발생하는 모든 로그를 실시간으로 수집하는 스크립트

echo "🚀 워크플로 생성 테스트 및 로그 수집"
echo "====================================="

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 디렉토리 생성
mkdir -p logs

# 타임스탬프
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo -e "${BLUE}1. 현재 시스템 상태 확인${NC}"
echo "================================"

# API 상태 확인
echo "API 상태 확인:"
curl -s http://localhost:8000/health > logs/health_check_$TIMESTAMP.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Backend API 응답 정상"
    cat logs/health_check_$TIMESTAMP.log
else
    echo "❌ Backend API 응답 없음"
fi

echo ""
echo "API v1 상태 확인:"
curl -s http://localhost:8000/api/v1/status > logs/api_status_$TIMESTAMP.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ API v1 응답 정상"
    cat logs/api_status_$TIMESTAMP.log
else
    echo "❌ API v1 응답 없음"
fi

echo ""
echo -e "${BLUE}2. 워크플로 생성 테스트${NC}"
echo "=========================="

# 워크플로 생성 API 호출
echo "워크플로 생성 요청 중..."
curl -X POST "http://localhost:8000/api/v1/workflows/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "할일 관리앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해.",
    "project_name": "todo-app-test"
  }' \
  -v > logs/workflow_creation_$TIMESTAMP.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 워크플로 생성 요청 완료"
    echo "응답 내용:"
    cat logs/workflow_creation_$TIMESTAMP.log
    
    # 워크플로 ID 추출 시도
    WORKFLOW_ID=$(grep -o '"id":"[^"]*"' logs/workflow_creation_$TIMESTAMP.log | cut -d'"' -f4)
    
    if [ ! -z "$WORKFLOW_ID" ]; then
        echo ""
        echo "워크플로 ID: $WORKFLOW_ID"
        
        echo ""
        echo -e "${BLUE}3. 워크플로 상태 모니터링${NC}"
        echo "============================"
        
        # 10초간 워크플로 상태 체크
        for i in {1..10}; do
            echo "상태 체크 $i/10..."
            curl -s "http://localhost:8000/api/v1/workflows/$WORKFLOW_ID" > logs/workflow_status_${TIMESTAMP}_${i}.log 2>&1
            
            if [ $? -eq 0 ]; then
                echo "응답 받음:"
                cat logs/workflow_status_${TIMESTAMP}_${i}.log
                echo ""
            else
                echo "응답 실패"
            fi
            
            sleep 2
        done
    fi
    
else
    echo "❌ 워크플로 생성 요청 실패"
    cat logs/workflow_creation_$TIMESTAMP.log
fi

echo ""
echo -e "${BLUE}4. 로그 파일 생성 완료${NC}"
echo "======================="
echo "생성된 로그 파일들:"
ls -la logs/*$TIMESTAMP*

echo ""
echo -e "${YELLOW}💡 디버깅 정보:${NC}"
echo "로그 파일 위치: ./logs/"
echo "최신 백엔드 로그: tail -f logs/backend_debug.log"
echo "워크플로 생성 로그: cat logs/workflow_creation_$TIMESTAMP.log"
echo "상태 체크 로그: cat logs/workflow_status_${TIMESTAMP}_*.log"
