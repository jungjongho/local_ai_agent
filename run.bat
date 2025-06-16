@echo off
REM Local AI Agent 실행 스크립트 (Windows)

echo 🤖 Local AI Agent 시작 중...

REM 환경 변수 확인
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다. .env.example을 복사하여 설정하세요.
    copy .env.example .env
    echo 📝 .env 파일이 생성되었습니다. OpenAI API 키를 설정하세요.
    pause
    exit /b 1
)

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다. Python 3.8 이상을 설치하세요.
    pause
    exit /b 1
)

REM 가상환경 생성 및 활성화
if not exist "venv" (
    echo 📦 가상환경 생성 중...
    python -m venv venv
)

echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치
echo 📥 의존성 설치 중...
pip install -r requirements.txt

REM 데이터 디렉토리 확인
if not exist "data\cache" mkdir data\cache
if not exist "data\logs" mkdir data\logs

REM OpenAI API 키 확인
findstr /C:"your_openai_api_key_here" .env >nul
if not errorlevel 1 (
    echo ⚠️  OpenAI API 키가 설정되지 않았습니다.
    echo 📝 .env 파일에서 OPENAI_API_KEY를 설정하세요.
    echo.
    echo 설정 후 다시 실행하세요: run.bat
    pause
    exit /b 1
)

REM 서버 시작
echo 🚀 서버 시작 중...
echo 📱 웹 인터페이스: http://localhost:8000/static/index.html
echo 📚 API 문서: http://localhost:8000/docs
echo.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

cd backend
python main.py

pause
