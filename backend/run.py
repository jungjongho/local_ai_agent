#!/usr/bin/env python3
"""
멀티 AI 에이전트 웹서비스 생성 시스템 - 백엔드 실행 스크립트

이 스크립트는 다음을 수행합니다:
1. 환경 설정 검증 (.env, 가상환경)
2. 의존성 설치 확인 
3. 워크스페이스 디렉토리 생성
4. FastAPI 서버 실행

사용법:
    cd backend && python run.py
    또는
    cd backend && python -m app.main
"""

import os
import sys
import subprocess
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """환경 설정 확인"""
    current_dir = Path.cwd()
    
    # 현재 디렉토리가 backend 인지 확인
    if current_dir.name != "backend":
        logger.error("❌ 이 스크립트는 backend 디렉토리에서 실행해야 합니다.")
        logger.error(f"현재 위치: {current_dir}")
        logger.error("실행 방법: cd backend && python run.py")
        return False
    
    # .env 파일 확인
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("⚠️  .env 파일이 없습니다. .env.example을 복사합니다...")
        if Path(".env.example").exists():
            subprocess.run(["cp", ".env.example", ".env"], check=True)
            logger.info("✅ .env 파일이 생성되었습니다.")
            logger.warning("🔑 .env 파일을 열어서 OPENAI_API_KEY를 설정하세요.")
        else:
            logger.error("❌ .env.example 파일을 찾을 수 없습니다.")
            return False
    
    return True

def setup_virtual_environment():
    """가상환경 설정"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        logger.info("🐍 Python 가상환경을 생성합니다...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        logger.info("✅ 가상환경이 생성되었습니다.")
    
    # 가상환경 실행 파일 경로 확인
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # macOS/Linux
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    if not python_exe.exists():
        logger.error("❌ 가상환경의 Python을 찾을 수 없습니다.")
        return None, None
    
    return python_exe, pip_exe

def install_dependencies(pip_exe):
    """의존성 설치"""
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        logger.info("📦 의존성을 설치합니다...")
        try:
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], 
                         check=True, capture_output=True, text=True)
            logger.info("✅ 의존성 설치 완료")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ 의존성 설치 실패: {e.stderr}")
            return False
    return True

def setup_workspace():
    """워크스페이스 디렉토리 생성"""
    workspace_dir = Path("../workspace/generated_projects")
    workspace_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 워크스페이스 생성: {workspace_dir.absolute()}")

def run_server(python_exe):
    """서버 실행"""
    logger.info("🚀 백엔드 서버를 시작합니다...")
    logger.info("📍 URL: http://localhost:8025")
    logger.info("📚 API 문서: http://localhost:8025/docs")
    logger.info("❤️  헬스 체크: http://localhost:8025/health")
    logger.info("⏹️  중지하려면 Ctrl+C를 누르세요")
    logger.info("")
    
    try:
        # app 모듈로 실행하여 import 문제 해결
        subprocess.run([
            str(python_exe), "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8025",
            "--reload-dir", "app"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("\n🛑 백엔드 서버가 중지되었습니다.")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 서버 실행 중 오류 발생: {e}")
        return False
    
    return True

def main():
    """메인 실행 함수"""
    try:
        # 1. 환경 검증
        if not check_environment():
            sys.exit(1)
        
        # 2. 가상환경 설정
        python_exe, pip_exe = setup_virtual_environment()
        if not python_exe:
            sys.exit(1)
        
        # 3. 의존성 설치
        if not install_dependencies(pip_exe):
            sys.exit(1)
        
        # 4. 워크스페이스 설정
        setup_workspace()
        
        # 5. 서버 실행
        if not run_server(python_exe):
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ 예상치 못한 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
