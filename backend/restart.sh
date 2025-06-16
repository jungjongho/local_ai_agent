#!/bin/bash
# 캐시 정리 및 서버 재시작 스크립트

echo "🧹 Python 캐시 정리 중..."

# __pycache__ 디렉토리 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# .pyc 파일 삭제
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ 캐시 정리 완료!"

echo "🚀 서버 실행 중..."
python main.py
