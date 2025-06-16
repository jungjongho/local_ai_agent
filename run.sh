#!/bin/bash

# Local AI Agent 실행 스크립트

echo "🤖 Local AI Agent 시작 중..."

# 환경 변수 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 설정하세요."
    cp .env.example .env
    echo "📝 .env 파일이 생성되었습니다. OpenAI API 키를 설정하세요."
    exit 1
fi

# Python 버전 확인
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 이상이 필요합니다. 현재 버전: $python_version"
    exit 1
fi

# 가상환경 생성 및 활성화
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치
echo "📥 의존성 설치 중..."
pip install -r requirements.txt

# 데이터 디렉토리 확인
mkdir -p data/cache data/logs

# OpenAI API 키 확인
if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  OpenAI API 키가 설정되지 않았습니다."
    echo "📝 .env 파일에서 OPENAI_API_KEY를 설정하세요."
    echo ""
    echo "설정 후 다시 실행하세요: ./run.sh"
    exit 1
fi

# 서버 시작
echo "🚀 서버 시작 중..."
echo "📱 웹 인터페이스: http://localhost:8000/static/index.html"
echo "📚 API 문서: http://localhost:8000/docs"
echo ""
echo "종료하려면 Ctrl+C를 누르세요."
echo ""

cd backend
python main.py
