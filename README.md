# 🚀 멀티 AI 에이전트 웹서비스 생성 시스템

**사용자 입력 한 줄로 실제 로컬 파일 시스템에 완전한 웹서비스(React + FastAPI)를 자동 생성하는 멀티 AI 에이전트 시스템**

## 📋 프로젝트 개요

이 시스템은 5개의 전문 AI 에이전트가 협력하여 사용자의 간단한 요청을 완전한 웹 애플리케이션으로 자동 변환합니다:

- **PM Agent**: 프로젝트 관리 및 요구사항 분석
- **UI/UX Agent**: 사용자 인터페이스 및 경험 설계
- **Frontend Agent**: React + TypeScript 코드 생성
- **Backend Agent**: FastAPI + Python 코드 생성  
- **DevOps Agent**: Docker, 환경설정, 배포 스크립트 생성

## 🏗️ 시스템 아키텍처

```
User Input → Orchestrator → [PM → UI/UX → Frontend → Backend → DevOps] → MCP Tools → 실제 파일 생성
```

### 핵심 기술 스택

**Backend**
- FastAPI (웹 API 서버)
- MCP (Model Context Protocol) - 실제 파일 시스템 접근
- SQLite (워크플로 및 프로젝트 데이터)
- OpenAI GPT-4 (AI 에이전트 엔진)

**Frontend**
- React + TypeScript (사용자 인터페이스)
- TailwindCSS (스타일링)
- Vite (빌드 도구)
- WebSocket (실시간 통신)

**DevOps**
- Docker (컨테이너화)
- Git (버전 관리)
- 환경변수 관리

## 🚀 빠른 시작

### 시스템 요구사항

- **Python 3.8+** (권장: 3.11+)
- **Node.js 16+** (권장: 18+)
- **npm** 또는 **yarn**
- **Git**
- **Docker** (선택사항)

### 💡 실행 방법

#### 방법 1: 전체 시스템 자동 실행 (권장)
```bash
# 저장소 클론
git clone <repository-url>
cd local_ai_agent

# 실행 권한 부여
chmod +x start.sh stop.sh

# 환경변수 설정
cp backend/.env.example backend/.env
# backend/.env 파일을 열어서 OPENAI_API_KEY를 설정하세요

# 전체 시스템 시작 (자동으로 의존성 설치 및 서버 시작)
./start.sh
```

#### 방법 2: 개별 서비스 실행 (개발용)

**Backend 실행**
```bash
cd backend
chmod +x dev.sh
./dev.sh
```

**Frontend 실행** (새 터미널)
```bash
cd frontend  
chmod +x dev.sh
./dev.sh
```

#### 방법 3: 수동 실행 (문제 해결용)

**Backend**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # 그리고 OPENAI_API_KEY 설정
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

### 🌐 시스템 접속

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000  
- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health

### 🛑 시스템 중지

```bash
./stop.sh
```

## 🔧 문제 해결

### ⚠️ 자주 발생하는 문제들

#### 1. Backend Import 오류
```
ImportError: attempted relative import with no known parent package
```
**해결**: 다음 명령으로 실행하세요
```bash
cd backend
python -m uvicorn app.main:app --reload
```

#### 2. Frontend TypeScript 설정 오류
```
tsconfig.node.json not found
```
**해결**: `frontend/tsconfig.node.json` 파일이 자동으로 생성됩니다

#### 3. 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# 프로세스 종료
kill -9 <PID>
```

#### 4. 환경변수 누락
```bash
# .env 파일 확인 및 생성
cd backend
cp .env.example .env
# 에디터로 .env 파일을 열어서 OPENAI_API_KEY 설정
```

### 📚 상세한 문제 해결 가이드

문제가 지속되는 경우 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 파일을 참조하세요.

## 🎯 사용 예시

### 입력
```
"온라인 할일 관리 앱을 만들어줘. 할일 추가, 완료 체크, 삭제 기능이 필요해."
```

### 출력 (5분 이내 자동 생성)
```
workspace/generated_projects/todo-app-20241201/
├── frontend/                 # React 앱
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   ├── package.json
│   └── README.md
├── backend/                  # FastAPI 앱
│   ├── app/
│   │   ├── models/
│   │   ├── routers/
│   │   └── main.py
│   ├── requirements.txt
│   └── README.md
├── docker-compose.yml        # 배포 설정
├── .env.example             # 환경변수
├── run.sh                   # 실행 스크립트
└── README.md               # 프로젝트 문서
```

### 자동 실행
```bash
cd workspace/generated_projects/todo-app-20241201
./run.sh

# → Frontend: http://localhost:3025
# → Backend: http://localhost:8025
# → 즉시 사용 가능한 웹앱!
```

## 🛠️ 주요 기능

### ✅ 완전 자동화된 웹서비스 생성
- 한 줄 입력으로 완전한 Full-Stack 웹 애플리케이션 생성
- Frontend-Backend 완전 연동
- 즉시 실행 가능한 상태로 생성

### ✅ 실시간 진행상황 모니터링
- WebSocket 기반 실시간 워크플로 추적
- 각 에이전트의 작업 상태 시각화
- 오류 발생 시 명확한 피드백

### ✅ 프로젝트 관리 기능
- 생성된 프로젝트 목록 및 상세 정보
- 프로젝트 시작/중지 제어
- 파일 구조 탐색 및 로그 조회

### ✅ MCP 기반 파일 시스템 접근
- 실제 로컬 파일 시스템에 프로젝트 생성
- Git 저장소 자동 초기화
- Docker 환경 설정 자동 생성

## 📁 프로젝트 구조

```
local_ai_agent/
├── backend/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── agents/          # AI 에이전트들
│   │   ├── api/             # API 라우터
│   │   ├── core/            # 핵심 설정
│   │   ├── mcp/             # MCP 클라이언트
│   │   ├── models/          # 데이터 모델
│   │   └── workflow_manager.py
│   ├── requirements.txt
│   ├── main.py
│   ├── run.py              # 개선된 실행 스크립트
│   └── dev.sh              # 개발용 실행 스크립트
├── frontend/                 # React 프론트엔드
│   ├── src/
│   │   ├── components/      # UI 컴포넌트
│   │   ├── pages/           # 페이지 컴포넌트
│   │   ├── services/        # API 서비스
│   │   └── types/           # TypeScript 타입
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json   # 새로 추가됨
│   ├── vite.config.ts       # 개선됨
│   ├── run.js              # Node.js 실행 스크립트
│   └── dev.sh              # 개발용 실행 스크립트
├── workspace/               # 생성된 프로젝트들
│   └── generated_projects/
├── logs/                    # 로그 파일들
├── docker-compose.yml       # Docker 설정
├── start.sh                # 전체 시스템 시작 (개선됨)
├── stop.sh                 # 중지 스크립트
├── TROUBLESHOOTING.md      # 문제 해결 가이드
└── README.md
```

## 🔧 개발 가이드

### 환경변수 설정

`backend/.env` 파일에서 다음 변수들을 설정하세요:

```env
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# 환경 설정
ENVIRONMENT=development
DEBUG=true

# 데이터베이스
DATABASE_URL=sqlite:///./app.db

# 작업공간
WORKSPACE_DIR=../workspace

# CORS 설정
CORS_ORIGINS=["http://localhost:3000"]
```

### Docker로 실행

```bash
# Docker Compose로 전체 시스템 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 개별 서비스 개발 모드 실행

**Backend 개발 서버**
```bash
cd backend
./dev.sh
# 또는
python run.py
```

**Frontend 개발 서버**
```bash
cd frontend
./dev.sh
# 또는  
node run.js
# 또는
npm run dev
```

## 🧪 테스트

### API 테스트
```bash
# 헬스 체크
curl http://localhost:8000/health

# API 상태 확인
curl http://localhost:8000/api/v1/status

# 프로젝트 목록
curl http://localhost:8000/api/v1/projects/

# 워크플로 생성
curl -X POST http://localhost:8000/api/v1/workflows/ \
  -H "Content-Type: application/json" \
  -d '{"user_input": "간단한 블로그 만들어줘", "project_name": "my-blog"}'
```

### 서비스 연결 테스트
```bash
# Frontend에서 Backend API 연결 확인
curl http://localhost:3000/api/health
```

## 📊 시스템 모니터링

### 실시간 로그 확인
```bash
# 전체 시스템 로그 (start.sh로 실행 시)
tail -f logs/backend.log
tail -f logs/frontend.log

# 개별 실행 시 터미널에서 직접 확인
```

### 시스템 상태 확인
```bash
# 프로세스 확인
ps aux | grep uvicorn  # Backend
ps aux | grep vite     # Frontend

# 포트 사용 확인
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# 디스크 사용량 확인
du -sh workspace/generated_projects/
```

## 🎊 성공 지표

### 기능적 지표
- ✅ 5분 이내 완전한 웹서비스 생성
- ✅ 생성된 프로젝트 즉시 실행 가능
- ✅ Frontend-Backend 완전 연동

### 기술적 지표
- ✅ MCP를 통한 실제 파일 시스템 접근
- ✅ 환경변수 기반 설정 관리
- ✅ Docker 기반 원클릭 배포
- ✅ 안정적인 import 구조 및 모듈 실행

### 사용자 경험 지표
- ✅ 비개발자도 웹서비스 생성 가능
- ✅ 실시간 진행상황 시각화
- ✅ 명확한 오류 메시지 및 복구 방안
- ✅ 다양한 실행 방법 제공 (자동/수동/개발)

## 🔄 업데이트 및 개선사항

### v1.1.0 업데이트 (현재)
- ✅ **Backend import 문제 해결**: 상대 import를 절대 import로 변경
- ✅ **Frontend TypeScript 설정 개선**: `tsconfig.node.json` 추가
- ✅ **다양한 실행 방법 제공**: 자동/개발/수동 실행 스크립트
- ✅ **개선된 Vite 설정**: 더 안정적인 개발 서버 설정
- ✅ **포괄적인 문제 해결 가이드**: `TROUBLESHOOTING.md` 추가
- ✅ **실행 권한 자동 설정**: 스크립트 파일들의 실행 권한 관리
- ✅ **로그 시스템 개선**: 구조화된 로깅 및 모니터링

## 🤝 기여 가이드

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 개발 환경 설정
```bash
# 개발용 브랜치 생성
git checkout -b feature/new-feature

# 의존성 설치 및 개발 서버 실행
./start.sh

# 변경사항 테스트
curl http://localhost:8000/health
```

## 📝 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 지원 및 문제 해결

### 빠른 해결 체크리스트

1. **시스템 요구사항 확인**
   - Python 3.8+ 설치됨
   - Node.js 16+ 설치됨
   - 충분한 디스크 공간 (최소 1GB)

2. **환경변수 설정 확인**
   - `backend/.env` 파일 존재
   - `OPENAI_API_KEY` 설정됨

3. **포트 충돌 확인**
   - 3000번, 8000번 포트 사용 가능

4. **권한 문제 확인**
   - 스크립트 파일들이 실행 가능
   - 워크스페이스 디렉토리 쓰기 권한

### 문제 보고

문제가 발생하거나 질문이 있으시면:

1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** 먼저 확인
2. **로그 파일** 확인 (`logs/` 디렉토리)
3. **[Issues](https://github.com/your-repo/issues)**에 다음 정보와 함께 등록:
   - 운영체제 및 버전
   - Python, Node.js 버전
   - 오류 메시지 및 로그
   - 재현 방법

## 📞 연락처

**개발팀**: AI Agent Development Team
**이메일**: support@ai-agent-system.com
**문서**: [GitHub Wiki](https://github.com/your-repo/wiki)

---

**Made with ❤️ by AI Agent Team**

*"한 줄의 아이디어를 완전한 웹서비스로"*
