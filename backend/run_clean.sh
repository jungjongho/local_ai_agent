#!/bin/bash

echo "🧹 완전한 캐시 정리 중..."

# 현재 디렉토리와 하위 디렉토리의 모든 __pycache__ 제거
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# .pyc 파일 제거  
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# .pyo 파일 제거
find . -type f -name "*.pyo" -delete 2>/dev/null || true

echo "✅ 캐시 정리 완료!"
echo ""
echo "🚀 서버 실행 중..."
echo "📍 URL: http://localhost:8000"
echo "📚 API 문서: http://localhost:8000/docs"
echo ""

python main.py
