# 🔧 문제 해결 가이드

이 문서는 멀티 AI 에이전트 웹서비스 생성 시스템에서 발생할 수 있는 문제들과 해결 방법을 안내합니다.

## ✅ 해결된 문제들

### 1. Frontend 문제: `tsconfig.node.json` 파일 누락
**문제**: Vite에서 `tsconfig.node.json` 파일을 찾을 수 없음
**해결**: `frontend/tsconfig.node.json` 파일 생성됨

### 2. Backend 문제: 상대 import 오류
**문제**: `ImportError: attempted relative import with no known parent package`
**해결**: 
- `main.py`에서 상대 import를 절대 import로 변경
- 패키지 실행 방식으로 수정: `python -m uvicorn app.main:app`

## 🚀 실행 방법

### 방법 1: 전체 시스템 실행 (권장)
```bash
# 프로젝트 루트에서
chmod +x start.sh
./start.sh
```

### 방법 2: 개별 서비스 실행

#### Backend 실행
```bash
cd backend
chmod +x dev.sh
./dev.sh
```

#### Frontend 실행
```bash
cd frontend
chmod +x dev.sh
./dev.sh
```

### 방법 3: Python/Node 직접 실행

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🔍 문제 진단

### Backend 문제 진단
```bash
cd backend

# 1. Python 버전 확인
python3 --version

# 2. 가상환경 확인
ls -la venv/

# 3. 의존성 확인
source venv/bin/activate
pip list

# 4. 환경변수 확인
cat .env

# 5. 앱 구조 확인
python -c "import app; print(app.__file__)"
```

### Frontend 문제 진단
```bash
cd frontend

# 1. Node.js 버전 확인
node --version
npm --version

# 2. 의존성 확인
ls -la node_modules/

# 3. TypeScript 설정 확인
cat tsconfig.json
cat tsconfig.node.json

# 4. Vite 설정 확인
cat vite.config.ts
```

## 🛠️ 일반적인 문제 해결

### 1. 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# 프로세스 종료
kill -9 <PID>
```

### 2. 권한 문제
```bash
# 실행 권한 부여
chmod +x start.sh stop.sh
chmod +x frontend/dev.sh backend/dev.sh
chmod +x frontend/run.js backend/run.py
```

### 3. 의존성 문제
```bash
# Backend 의존성 재설치
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### 4. 환경변수 문제
```bash
# .env 파일 확인
cd backend
cp .env.example .env
# 에디터로 .env 파일 열어서 OPENAI_API_KEY 설정
```

## 📊 서비스 확인

### 서비스 상태 확인
```bash
# Backend 헬스 체크
curl http://localhost:8000/health

# Frontend 접근 확인
curl http://localhost:3000

# API 문서 확인
open http://localhost:8000/docs
```

### 로그 확인
```bash
# 전체 시스템 실행 시
tail -f logs/backend.log
tail -f logs/frontend.log

# 개별 실행 시 콘솔에서 직접 확인
```

## 🔄 재시작 방법

### 전체 시스템 재시작
```bash
./stop.sh
./start.sh
```

### 개별 서비스 재시작
```bash
# Ctrl+C로 중지 후
cd backend && ./dev.sh
cd frontend && ./dev.sh
```

## 📞 추가 도움

문제가 지속되는 경우:
1. 로그 파일 확인
2. 시스템 요구사항 재확인 (Python 3.8+, Node.js 16+)
3. 방화벽 설정 확인
4. 프로젝트를 새로 clone하여 재시도

## 🎯 성공 지표

다음이 모두 동작하면 성공:
- ✅ http://localhost:8000/health - Backend 헬스 체크
- ✅ http://localhost:8000/docs - API 문서 접근
- ✅ http://localhost:3000 - Frontend 접근
- ✅ API 호출이 Frontend에서 Backend로 정상 연결
