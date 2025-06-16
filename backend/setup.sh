#!/bin/bash
# Backend 의존성 설치 및 서버 실행 스크립트

echo "🚀 Local AI Agent Backend 설정 중..."

# 가상환경 활성화 확인
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 가상환경이 활성화되어 있습니다: $VIRTUAL_ENV"
else
    echo "❌ 가상환경이 활성화되지 않았습니다."
    echo "다음 명령어로 가상환경을 활성화해주세요:"
    echo "source venv/bin/activate"
    exit 1
fi

# 의존성 설치
echo "📦 의존성 패키지 설치 중..."
pip install -r requirements.txt

# .env 파일 확인
if [ ! -f .env ]; then
    echo "⚠️ .env 파일이 없습니다."
    if [ -f ..//.env.example ]; then
        echo "📄 .env.example을 참고하여 .env 파일을 생성해주세요."
        echo "cp ../.env.example .env"
    fi
else
    echo "✅ .env 파일이 존재합니다."
fi

echo "🎯 설정이 완료되었습니다!"
echo "서버를 실행하려면: python main.py"
