# Local AI Agent Makefile
# 프로젝트 관리를 위한 유틸리티 명령어들

.PHONY: help run dev clean test install docs

# 기본 변수
PYTHON := python3
PIP := pip3
PROJECT_DIR := $(shell pwd)
BACKEND_DIR := backend
VENV_DIR := venv

help: ## 사용 가능한 명령어들을 보여줍니다
	@echo "🚀 Local AI Agent - 사용 가능한 명령어:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## 필요한 패키지들을 설치합니다
	@echo "📦 패키지 설치 중..."
	$(PIP) install -r requirements.txt

run: ## 서버를 실행합니다 (권장)
	@echo "🚀 Local AI Agent 서버 실행..."
	@echo "📂 프로젝트 디렉토리: $(PROJECT_DIR)"
	$(PYTHON) run_server.py

dev: ## 개발 모드로 서버를 실행합니다
	@echo "🔧 개발 모드로 서버 실행..."
	$(PYTHON) run_server.py

backend-direct: ## backend 디렉토리에서 직접 실행 (수정된 import 사용)
	@echo "⚠️  backend 디렉토리에서 직접 실행..."
	cd $(BACKEND_DIR) && $(PYTHON) main.py

clean: ## 캐시와 임시 파일들을 정리합니다
	@echo "🧹 프로젝트 정리 중..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

test: ## 테스트를 실행합니다
	@echo "🧪 테스트 실행..."
	$(PYTHON) -m pytest tests/ -v

docs: ## API 문서를 확인합니다
	@echo "📚 API 문서 정보:"
	@echo "  • Swagger UI: http://localhost:8000/docs"
	@echo "  • ReDoc: http://localhost:8000/redoc"

check-env: ## 환경 설정을 확인합니다
	@echo "🔍 환경 설정 확인:"
	@echo "  • Python 버전: $(shell $(PYTHON) --version)"
	@echo "  • 프로젝트 경로: $(PROJECT_DIR)"
	@echo "  • 가상환경 활성화 여부: $(if $(VIRTUAL_ENV),✅ 활성화됨 ($(VIRTUAL_ENV)),❌ 비활성화됨)"
	@if [ -f .env ]; then echo "  • .env 파일: ✅ 존재함"; else echo "  • .env 파일: ❌ 없음 (.env.example을 참고하세요)"; fi

# 기본 타겟
default: run
