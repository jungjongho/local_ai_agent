from typing import Dict, Any, List, Optional
import json
import os
import subprocess
from pathlib import Path
from datetime import datetime
from .base import EnhancedBaseAgent
import asyncio


class DevOpsAgent(EnhancedBaseAgent):
    """DevOps 에이전트 - Docker, 환경설정, 배포 스크립트 생성"""
    
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="devops",
            description="Docker 설정, 환경변수, 배포 스크립트를 생성하는 DevOps 에이전트",
            model=model
        )
    
    def get_system_prompt(self) -> str:
        return """당신은 전문 DevOps 엔지니어 AI 에이전트입니다.

주요 역할:
1. Docker 설정 파일 생성 (Dockerfile, docker-compose.yml)
2. 환경변수 파일 생성 (.env.example, .env.local)
3. 실행 스크립트 생성 (run.sh, start.sh, stop.sh)
4. 개발/운영 환경 설정
5. 포트 관리 및 서비스 시작

기술 스택:
- Frontend: React + Vite (포트: 3000번대)
- Backend: FastAPI (포트: 8000번대)
- Database: SQLite (로컬 파일)

Docker 설정 특징:
- 멀티스테이지 빌드 사용
- 개발/운영 환경 분리
- 볼륨 마운트로 실시간 개발
- 포트 충돌 방지

반드시 실제 동작하는 설정 파일을 생성해야 합니다."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """DevOps 에이전트 실행"""
        try:
            project_plan = input_data.get("project_plan", {})
            frontend_files = input_data.get("frontend_files", {})
            backend_files = input_data.get("backend_files", {})
            
            project_name = project_plan.get("project_name", "web-app")
            
            # 포트 할당
            ports = await self._allocate_ports()
            
            # DevOps 파일들 생성
            devops_files = {}
            
            # 1. Docker 설정
            devops_files.update(await self._create_docker_config(project_name, ports))
            
            # 2. 환경변수 파일
            devops_files.update(await self._create_env_files(project_name, ports))
            
            # 3. 실행 스크립트
            devops_files.update(await self._create_scripts(project_name, ports))
            
            # 4. 프로젝트 메타데이터
            devops_files.update(await self._create_project_metadata(project_plan, ports))
            
            return {
                "devops_files": devops_files,
                "ports": ports,
                "deployment_config": {
                    "project_name": project_name,
                    "frontend_url": f"http://localhost:{ports['frontend']}",
                    "backend_url": f"http://localhost:{ports['backend']}",
                    "database_file": f"{project_name}.db"
                }
            }
            
        except Exception as e:
            raise Exception(f"DevOps 에이전트 실행 실패: {str(e)}")
    
    async def _allocate_ports(self) -> Dict[str, int]:
        """사용 가능한 포트 할당"""
        try:
            # 포트 범위 설정
            frontend_base = 3000
            backend_base = 8000
            
            # 사용 중인 포트 확인
            frontend_port = await self._find_available_port(frontend_base, frontend_base + 100)
            backend_port = await self._find_available_port(backend_base, backend_base + 100)
            
            return {
                "frontend": frontend_port,
                "backend": backend_port
            }
            
        except Exception:
            # 기본 포트 반환
            return {
                "frontend": 3025,  # 일반적이지 않은 포트 사용
                "backend": 8025
            }
    
    async def _find_available_port(self, start_port: int, end_port: int) -> int:
        """사용 가능한 포트 찾기"""
        import socket
        
        for port in range(start_port, end_port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        # 모든 포트가 사용 중이면 기본값 반환
        return start_port + 25
    
    async def _create_docker_config(self, project_name: str, ports: Dict[str, int]) -> Dict[str, str]:
        """Docker 설정 파일 생성"""
        files = {}
        
        # Frontend Dockerfile
        files["frontend/Dockerfile"] = f"""# Frontend Dockerfile
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
"""

        # Backend Dockerfile
        files["backend/Dockerfile"] = f"""# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

        # Nginx config for frontend
        files["frontend/nginx.conf"] = """events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
"""

        # Docker Compose
        files["docker-compose.yml"] = f"""version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "{ports['frontend']}:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:{ports['backend']}
    volumes:
      - ./frontend:/app
      - /app/node_modules
    networks:
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "{ports['backend']}:8000"
    environment:
      - DATABASE_URL=sqlite:///./data/{project_name}.db
      - CORS_ORIGINS=http://localhost:{ports['frontend']}
    volumes:
      - ./backend:/app
      - ./data:/app/data
    networks:
      - app-network

  # Development services
  frontend-dev:
    profiles:
      - dev
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "{ports['frontend']}:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:{ports['backend']}
    command: npm run dev -- --host
    networks:
      - app-network

  backend-dev:
    profiles:
      - dev
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "{ports['backend']}:8000"
    volumes:
      - ./backend:/app
      - ./data:/app/data
    environment:
      - DATABASE_URL=sqlite:///./data/{project_name}.db
      - CORS_ORIGINS=http://localhost:{ports['frontend']}
      - RELOAD=true
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  node_modules:
"""

        # Development Dockerfiles
        files["frontend/Dockerfile.dev"] = """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
"""

        files["backend/Dockerfile.dev"] = """FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"""

        return files
    
    async def _create_env_files(self, project_name: str, ports: Dict[str, int]) -> Dict[str, str]:
        """환경변수 파일 생성"""
        files = {}
        
        # 프로젝트 루트 .env.example
        files[".env.example"] = f"""# {project_name.upper()} Environment Variables

# Application
APP_NAME={project_name}
APP_VERSION=1.0.0
ENVIRONMENT=development

# Ports
FRONTEND_PORT={ports['frontend']}
BACKEND_PORT={ports['backend']}

# Database
DATABASE_URL=sqlite:///./data/{project_name}.db

# CORS
CORS_ORIGINS=http://localhost:{ports['frontend']}

# Security (Change these in production!)
SECRET_KEY=your-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-change-this

# External APIs (if needed)
# OPENAI_API_KEY=your-openai-api-key
# GOOGLE_API_KEY=your-google-api-key

# Email (if needed)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email
# SMTP_PASSWORD=your-password
"""

        # 프로젝트 루트 .env.local (개발용)
        files[".env.local"] = f"""# Local Development Environment
APP_NAME={project_name}
ENVIRONMENT=development
FRONTEND_PORT={ports['frontend']}
BACKEND_PORT={ports['backend']}
DATABASE_URL=sqlite:///./data/{project_name}.db
CORS_ORIGINS=http://localhost:{ports['frontend']}
SECRET_KEY=local-development-secret-key
JWT_SECRET=local-development-jwt-secret
"""

        # Frontend .env
        files["frontend/.env"] = f"""REACT_APP_API_URL=http://localhost:{ports['backend']}
REACT_APP_APP_NAME={project_name}
REACT_APP_VERSION=1.0.0
"""

        # Backend .env
        files["backend/.env"] = f"""DATABASE_URL=sqlite:///./data/{project_name}.db
CORS_ORIGINS=http://localhost:{ports['frontend']}
SECRET_KEY=local-development-secret-key
JWT_SECRET=local-development-jwt-secret
"""

        return files
    
    async def _create_scripts(self, project_name: str, ports: Dict[str, int]) -> Dict[str, str]:
        """실행 스크립트 생성"""
        files = {}
        
        # 메인 실행 스크립트
        files["run.sh"] = f"""#!/bin/bash

# {project_name} - 실행 스크립트
echo "🚀 {project_name} 시작 중..."

# 데이터 디렉토리 생성
mkdir -p data

# 환경변수 파일 확인
if [ ! -f .env.local ]; then
    echo "📋 환경변수 파일을 복사합니다..."
    cp .env.example .env.local
fi

# Docker Compose로 개발 환경 시작
echo "🐳 Docker 컨테이너를 시작합니다..."
docker-compose --profile dev up --build -d

# 서비스 시작 대기
echo "⏳ 서비스 시작을 기다리는 중..."
sleep 10

# 상태 확인
echo "📊 서비스 상태 확인 중..."
docker-compose ps

# 서비스 URL 출력
echo ""
echo "✅ {project_name} 시작 완료!"
echo "🌐 Frontend: http://localhost:{ports['frontend']}"
echo "🔧 Backend API: http://localhost:{ports['backend']}"
echo "📚 API 문서: http://localhost:{ports['backend']}/docs"
echo ""
echo "중지하려면: ./stop.sh"
echo "로그 확인: ./logs.sh"
"""

        # 중지 스크립트
        files["stop.sh"] = f"""#!/bin/bash

echo "🛑 {project_name} 중지 중..."

# Docker Compose로 서비스 중지
docker-compose --profile dev down

echo "✅ {project_name} 중지 완료!"
"""

        # 로그 확인 스크립트
        files["logs.sh"] = f"""#!/bin/bash

echo "📋 {project_name} 로그 확인"
echo "종료하려면 Ctrl+C를 누르세요"
echo ""

# 모든 서비스의 로그를 실시간으로 출력
docker-compose --profile dev logs -f
"""

        # 개발 환경 설정 스크립트
        files["setup-dev.sh"] = f"""#!/bin/bash

echo "🔧 {project_name} 개발 환경 설정 중..."

# Node.js 및 npm 버전 확인
echo "📦 Node.js 환경 확인..."
node --version
npm --version

# Python 환경 확인
echo "🐍 Python 환경 확인..."
python3 --version

# Docker 환경 확인
echo "🐳 Docker 환경 확인..."
docker --version
docker-compose --version

# 프론트엔드 의존성 설치
echo "📱 프론트엔드 의존성 설치..."
cd frontend
npm install
cd ..

# 백엔드 의존성 설치
echo "🔧 백엔드 의존성 설치..."
cd backend
pip install -r requirements.txt
cd ..

# 데이터 디렉토리 생성
mkdir -p data

# 환경변수 파일 복사
if [ ! -f .env.local ]; then
    cp .env.example .env.local
    echo "📋 환경변수 파일(.env.local)을 생성했습니다."
    echo "필요한 경우 설정을 수정해주세요."
fi

echo "✅ 개발 환경 설정 완료!"
echo "실행하려면: ./run.sh"
"""

        # 프로덕션 실행 스크립트
        files["run-prod.sh"] = f"""#!/bin/bash

echo "🚀 {project_name} 프로덕션 시작 중..."

# 환경변수 파일 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다. 프로덕션 환경변수를 설정해주세요."
    exit 1
fi

# Docker Compose로 프로덕션 환경 시작
docker-compose up --build -d

echo "✅ {project_name} 프로덕션 시작 완료!"
echo "🌐 서비스: http://localhost:{ports['frontend']}"
"""

        # 백업 스크립트
        files["backup.sh"] = f"""#!/bin/bash

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="{project_name}_backup_$TIMESTAMP"

echo "💾 {project_name} 백업 생성 중..."

# 백업 디렉토리 생성
mkdir -p $BACKUP_DIR

# 데이터베이스 백업
if [ -f "data/{project_name}.db" ]; then
    echo "📊 데이터베이스 백업 중..."
    cp "data/{project_name}.db" "$BACKUP_DIR/$BACKUP_NAME.db"
fi

# 환경변수 파일 백업
if [ -f ".env.local" ]; then
    echo "⚙️ 환경설정 백업 중..."
    cp ".env.local" "$BACKUP_DIR/$BACKUP_NAME.env"
fi

# 전체 프로젝트 아카이브
echo "📦 전체 프로젝트 아카이브 생성 중..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \\
    --exclude="node_modules" \\
    --exclude="__pycache__" \\
    --exclude=".git" \\
    --exclude="backups" \\
    .

echo "✅ 백업 완료: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
"""

        return files
    
    async def _create_project_metadata(self, project_plan: Dict[str, Any], ports: Dict[str, int]) -> Dict[str, str]:
        """프로젝트 메타데이터 파일 생성"""
        files = {}
        
        project_name = project_plan.get("project_name", "web-app")
        description = project_plan.get("description", "웹 애플리케이션")
        tech_stack = project_plan.get("tech_stack", {})
        
        # 메인 README.md
        files["README.md"] = f"""# {project_name}

{description}

## 🚀 빠른 시작

### 1. 개발 환경 설정
```bash
# 개발 환경 설정 (최초 1회)
chmod +x *.sh
./setup-dev.sh
```

### 2. 애플리케이션 실행
```bash
# 개발 서버 시작
./run.sh

# 또는 Docker 없이 로컬에서 실행
npm run dev:local
```

### 3. 접속
- 🌐 Frontend: http://localhost:{ports['frontend']}
- 🔧 Backend API: http://localhost:{ports['backend']}
- 📚 API 문서: http://localhost:{ports['backend']}/docs

## 📋 주요 기능

{self._format_features(project_plan.get('requirements', {}).get('main_features', []))}

## 🛠 기술 스택

### Frontend
- {tech_stack.get('frontend', 'React + TypeScript + TailwindCSS')}
- Vite (빌드 도구)
- Axios (HTTP 클라이언트)

### Backend  
- {tech_stack.get('backend', 'FastAPI + SQLAlchemy + SQLite')}
- Pydantic (데이터 검증)
- SQLite (데이터베이스)

### DevOps
- Docker & Docker Compose
- Nginx (프로덕션 웹서버)

## 📁 프로젝트 구조

```
{project_name}/
├── frontend/              # React 애플리케이션
│   ├── src/
│   │   ├── components/    # 재사용 컴포넌트
│   │   ├── pages/        # 페이지 컴포넌트
│   │   ├── services/     # API 호출 로직
│   │   └── types/        # TypeScript 타입 정의
│   ├── package.json
│   └── Dockerfile
├── backend/              # FastAPI 애플리케이션
│   ├── app/
│   │   ├── models/       # 데이터베이스 모델
│   │   ├── routers/      # API 라우터
│   │   ├── services/     # 비즈니스 로직
│   │   └── main.py       # 애플리케이션 진입점
│   ├── requirements.txt
│   └── Dockerfile
├── data/                 # 데이터베이스 파일
├── docker-compose.yml    # Docker 설정
├── .env.example         # 환경변수 템플릿
└── run.sh              # 실행 스크립트
```

## 🔧 개발 명령어

```bash
# 애플리케이션 시작
./run.sh

# 애플리케이션 중지
./stop.sh

# 로그 확인
./logs.sh

# 백업 생성
./backup.sh

# 프로덕션 실행
./run-prod.sh
```

## 🔍 API 문서

애플리케이션 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:{ports['backend']}/docs
- ReDoc: http://localhost:{ports['backend']}/redoc

## 🐛 문제 해결

### 포트 충돌
```bash
# 다른 포트 사용 중인 프로세스 확인
lsof -i :{ports['frontend']}
lsof -i :{ports['backend']}

# 프로세스 종료
kill -9 <PID>
```

### Docker 문제
```bash
# Docker 컨테이너 정리
docker-compose down
docker system prune -f

# 이미지 다시 빌드
docker-compose build --no-cache
```

### 권한 문제
```bash
# 스크립트 실행 권한 부여
chmod +x *.sh
```

## 📝 환경변수

주요 환경변수는 `.env.local` 파일에서 설정할 수 있습니다:

```env
# 포트 설정
FRONTEND_PORT={ports['frontend']}
BACKEND_PORT={ports['backend']}

# 데이터베이스
DATABASE_URL=sqlite:///./data/{project_name}.db

# CORS 설정
CORS_ORIGINS=http://localhost:{ports['frontend']}
```

## 🚀 배포

### Docker를 이용한 배포
```bash
# 프로덕션 환경변수 설정
cp .env.example .env
# .env 파일 편집

# 프로덕션 실행
./run-prod.sh
```

---

생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        # package.json template for local development
        files["package.json"] = f"""{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "{description}",
  "scripts": {{
    "dev:local": "concurrently \\"npm run dev:frontend\\" \\"npm run dev:backend\\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "cd backend && uvicorn main:app --reload --port {ports['backend']}",
    "build": "cd frontend && npm run build",
    "start": "./run.sh",
    "stop": "./stop.sh",
    "logs": "./logs.sh",
    "setup": "./setup-dev.sh"
  }},
  "devDependencies": {{
    "concurrently": "^8.2.0"
  }}
}}
"""

        # .gitignore
        files[".gitignore"] = """# Dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3
data/

# Build outputs
dist/
build/
.next/
.nuxt/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
.dockerignore

# Backup
backups/

# Testing
coverage/
.nyc_output/
.coverage

# Temporary files
tmp/
temp/
"""

        return files
    
    def _format_features(self, features: List[str]) -> str:
        """기능 목록을 마크다운으로 포맷팅"""
        if not features:
            return "- 기본 웹 애플리케이션 기능"
        
        return "\n".join([f"- {feature}" for feature in features])
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        required_fields = ["project_plan"]
        
        for field in required_fields:
            if field not in input_data:
                return False
        
        project_plan = input_data.get("project_plan", {})
        if not isinstance(project_plan, dict):
            return False
        
        return True
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """출력 데이터 검증"""
        required_fields = ["devops_files", "ports", "deployment_config"]
        
        for field in required_fields:
            if field not in output_data:
                return False
        
        # DevOps 파일 검증
        devops_files = output_data.get("devops_files", {})
        required_files = ["docker-compose.yml", "run.sh", ".env.example", "README.md"]
        
        for file_name in required_files:
            if file_name not in devops_files:
                return False
        
        return True
