# 🛠️ 개발자 실행 가이드

## 📋 개별 서비스 실행 방법

### 🔧 **백엔드 실행 (FastAPI)**

#### 방법 1: Python 스크립트 사용 (권장)
```bash
cd backend
python run.py
```

#### 방법 2: 직접 실행
```bash
cd backend

# 가상환경 생성 (최초 1회)
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어서 OPENAI_API_KEY 설정

# 서버 실행
uvicorn main:app --reload
```

**접속 URL:**
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs

---

### ⚛️ **프론트엔드 실행 (React + Vite)**

#### 방법 1: npm start
```bash
cd frontend
npm install  # 최초 1회
npm start
```

#### 방법 2: npm run dev
```bash
cd frontend
npm install  # 최초 1회
npm run dev
```

**접속 URL:**
- Frontend UI: http://localhost:3000

---

## 🚀 **전체 시스템 자동 실행**

개별 실행이 번거로우면 자동화 스크립트 사용:

```bash
# 모든 서비스 자동 시작
./start.sh

# 모든 서비스 중지
./stop.sh

# 시스템 테스트
./test.sh
```

---

## 📊 **개발 중 유용한 명령어**

### 백엔드 개발
```bash
# 데이터베이스 초기화
cd backend
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

# API 테스트
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/projects/

# 로그 확인
tail -f logs/backend.log
```

### 프론트엔드 개발
```bash
# 타입 체크
cd frontend
npm run lint

# 빌드 테스트
npm run build

# 프로덕션 프리뷰
npm run preview
```

---

## 🔧 **개발 환경 설정**

### 필수 요구사항
- Python 3.11+
- Node.js 18+
- npm 또는 yarn

### 권장 도구
- VS Code + Python + TypeScript 확장
- Git
- Docker (선택사항)

### 환경변수 설정
`backend/.env` 파일:
```env
OPENAI_API_KEY=your_api_key_here
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./app.db
WORKSPACE_DIR=./workspace
CORS_ORIGINS=["http://localhost:3000"]
```

---

## 🐛 **문제 해결**

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000  # 백엔드
lsof -i :3000  # 프론트엔드

# 프로세스 종료
kill -9 <PID>
```

### 의존성 문제
```bash
# 백엔드 의존성 재설치
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 프론트엔드 의존성 재설치
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### OpenAI API 키 오류
```bash
# .env 파일 확인
cat backend/.env

# API 키 테스트
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.openai.com/v1/models
```

---

## 📝 **개발 팁**

### 백엔드 개발
- `--reload` 옵션으로 코드 변경 시 자동 재시작
- `/docs` 엔드포인트에서 API 문서 확인
- SQLite 브라우저로 데이터베이스 확인

### 프론트엔드 개발
- Vite의 HMR(Hot Module Replacement) 활용
- React DevTools 사용 권장
- TailwindCSS 클래스 자동완성 활용

### 통합 개발
- 양쪽 모두 실행한 상태에서 개발
- CORS 설정이 올바른지 확인
- WebSocket 연결 상태 모니터링

---

이렇게 개별 실행하시면 각 서비스를 독립적으로 개발하고 디버깅할 수 있어서 더 편리합니다! 🚀
