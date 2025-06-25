#!/bin/bash

# 멀티 AI 에이전트 웹서비스 생성 시스템 테스트 스크립트

echo "🧪 멀티 AI 에이전트 웹서비스 생성 시스템 테스트 시작"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 테스트 함수 정의
test_api_endpoint() {
    local endpoint=$1
    local expected_status=${2:-200}
    local method=${3:-GET}
    
    echo -e "${BLUE}Testing ${method} ${endpoint}...${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/api_response.json "http://localhost:8000${endpoint}")
    else
        response=$(curl -s -w "%{http_code}" -X ${method} -o /tmp/api_response.json "http://localhost:8000${endpoint}")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✅ ${endpoint} - Status: ${response}${NC}"
        if [ -f "/tmp/api_response.json" ]; then
            cat /tmp/api_response.json | jq . 2>/dev/null || cat /tmp/api_response.json
        fi
        echo ""
        return 0
    else
        echo -e "${RED}❌ ${endpoint} - Expected: ${expected_status}, Got: ${response}${NC}"
        if [ -f "/tmp/api_response.json" ]; then
            cat /tmp/api_response.json
        fi
        echo ""
        return 1
    fi
}

# 서비스 상태 확인
check_services() {
    echo -e "${BLUE}🔍 서비스 상태 확인...${NC}"
    
    # Backend 포트 확인
    if netstat -tuln | grep -q ":8000 "; then
        echo -e "${GREEN}✅ Backend 서버 실행 중 (포트 8000)${NC}"
    else
        echo -e "${RED}❌ Backend 서버가 실행되지 않음 (포트 8000)${NC}"
        echo -e "${YELLOW}먼저 ./start.sh를 실행하세요.${NC}"
        exit 1
    fi
    
    # Frontend 포트 확인
    if netstat -tuln | grep -q ":3000 "; then
        echo -e "${GREEN}✅ Frontend 서버 실행 중 (포트 3000)${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend 서버가 실행되지 않음 (포트 3000)${NC}"
    fi
    
    echo ""
}

# API 테스트 실행
run_api_tests() {
    echo -e "${BLUE}🧪 API 엔드포인트 테스트...${NC}"
    
    # 기본 엔드포인트 테스트
    test_api_endpoint "/"
    test_api_endpoint "/health"
    test_api_endpoint "/api/v1/status"
    
    # 프로젝트 관련 API 테스트
    test_api_endpoint "/api/v1/projects/"
    test_api_endpoint "/api/v1/projects/workspace/info"
    test_api_endpoint "/api/v1/projects/workspace/requirements"
    
    # 워크플로 관련 API 테스트
    test_api_endpoint "/api/v1/workflows/"
    
    echo -e "${GREEN}🎉 API 테스트 완료!${NC}"
}

# 샘플 워크플로 생성 테스트
test_workflow_creation() {
    echo -e "${BLUE}🔬 샘플 워크플로 생성 테스트...${NC}"
    
    # 샘플 워크플로 데이터
    workflow_data='{
        "user_input": "간단한 할일 관리 앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해.",
        "project_name": "test-todo-app"
    }'
    
    echo "워크플로 생성 요청 중..."
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$workflow_data" \
        -o /tmp/workflow_response.json \
        "http://localhost:8000/api/v1/workflows/")
    
    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        echo -e "${GREEN}✅ 워크플로 생성 성공!${NC}"
        if [ -f "/tmp/workflow_response.json" ]; then
            workflow_id=$(cat /tmp/workflow_response.json | jq -r '.id' 2>/dev/null)
            echo "워크플로 ID: $workflow_id"
            cat /tmp/workflow_response.json | jq . 2>/dev/null || cat /tmp/workflow_response.json
        fi
    else
        echo -e "${RED}❌ 워크플로 생성 실패 - Status: ${response}${NC}"
        if [ -f "/tmp/workflow_response.json" ]; then
            cat /tmp/workflow_response.json
        fi
    fi
    
    echo ""
}

# 프론트엔드 접근성 테스트
test_frontend() {
    echo -e "${BLUE}🌐 프론트엔드 접근성 테스트...${NC}"
    
    frontend_response=$(curl -s -w "%{http_code}" -o /tmp/frontend_response.html "http://localhost:3000")
    
    if [ "$frontend_response" = "200" ]; then
        echo -e "${GREEN}✅ 프론트엔드 접근 가능 (http://localhost:3000)${NC}"
    else
        echo -e "${YELLOW}⚠️  프론트엔드 접근 불가 - Status: ${frontend_response}${NC}"
        echo -e "${YELLOW}Frontend 서버가 아직 시작되지 않았을 수 있습니다.${NC}"
    fi
    
    echo ""
}

# 시스템 정보 출력
print_system_info() {
    echo -e "${BLUE}📊 시스템 정보${NC}"
    echo "Current directory: $(pwd)"
    echo "Python version: $(python3 --version 2>/dev/null || echo 'Not found')"
    echo "Node.js version: $(node --version 2>/dev/null || echo 'Not found')"
    echo "npm version: $(npm --version 2>/dev/null || echo 'Not found')"
    echo "Docker version: $(docker --version 2>/dev/null || echo 'Not found')"
    echo ""
}

# 결과 요약
print_summary() {
    echo -e "${GREEN}📋 테스트 요약${NC}"
    echo -e "${GREEN}✅ Backend API: http://localhost:8000${NC}"
    echo -e "${GREEN}✅ API 문서: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}✅ Frontend UI: http://localhost:3000${NC}"
    echo ""
    echo -e "${BLUE}💡 다음 단계:${NC}"
    echo "1. 웹 브라우저에서 http://localhost:3000 접속"
    echo "2. 새로운 워크플로 생성 테스트"
    echo "3. 생성된 프로젝트 확인"
    echo ""
    echo -e "${YELLOW}📝 참고:${NC}"
    echo "- 로그 확인: tail -f logs/backend.log"
    echo "- 시스템 중지: ./stop.sh"
    echo "- 도움말: cat README.md"
}

# 메인 테스트 실행
main() {
    print_system_info
    check_services
    run_api_tests
    test_frontend
    test_workflow_creation
    print_summary
}

# 스크립트 실행
main

echo -e "${GREEN}🎉 테스트 완료!${NC}"
