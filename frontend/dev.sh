#!/bin/bash

# 개발용 간단 실행 스크립트 - Frontend Only

echo "⚛️ Frontend 개발 서버 시작"

# 현재 디렉토리 확인
if [ ! -f "package.json" ]; then
    echo "❌ frontend 디렉토리에서 실행해주세요."
    echo "실행 방법: cd frontend && ./dev.sh"
    exit 1
fi

# node_modules 확인
if [ ! -d "node_modules" ]; then
    echo "📦 의존성을 설치합니다..."
    npm install
fi

echo "🚀 Vite 개발 서버를 시작합니다..."
echo "📍 Frontend: http://localhost:3000"
echo "⏹️  중지하려면 Ctrl+C를 누르세요"
echo ""

npm run dev
