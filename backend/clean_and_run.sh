#!/bin/bash
echo "🧹 캐시 정리 중..."
find /Users/mac/Desktop/jongho_project/jongho_service/local_ai_agent/backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /Users/mac/Desktop/jongho_project/jongho_service/local_ai_agent/backend -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ 캐시 정리 완료!"
echo "🚀 서버 실행 중..."
cd /Users/mac/Desktop/jongho_project/jongho_service/local_ai_agent/backend
python main.py
