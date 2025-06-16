# Local AI Agent

🤖 GPT API 기반 로컬 AI 에이전트 시스템

## 📋 프로젝트 개요

Local AI Agent는 OpenAI GPT API를 활용한 확장 가능한 AI 에이전트 시스템입니다. Phase별 개발 계획에 따라 단계적으로 기능을 확장할 수 있도록 설계되었습니다.

### 🎯 주요 특징

- **Phase 1** (완료): GPT API 연동, 캐싱, 기본 채팅 기능
- **Phase 2** (완료): File System Tool, Agent 서비스, Function Calling
- **Phase 3** (예정): 시스템 통합 및 추가 도구
- **Phase 4** (예정): 고급 최적화 및 오프라인 기능

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 OpenAI API 키 설정
```

### 2. 환경 변수 설정

`.env` 파일에서 다음 설정을 수정하세요:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
SECRET_KEY=your_secret_key_here
```

### 3. 서버 실행

```bash
# 백엔드 서버 시작
cd backend
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 프론트엔드 접속

브라우저에서 `http://localhost:8000/static/index.html` 접속

## 📁 프로젝트 구조

```
local_ai_agent/
├── backend/                 # FastAPI 백엔드
│   ├── config/             # 설정 관리
│   ├── core/               # 핵심 모듈 (GPT, 캐시, 토큰)
│   ├── services/           # 비즈니스 로직
│   ├── api/                # API 엔드포인트
│   ├── models/             # 데이터 모델
│   └── utils/              # 유틸리티
├── frontend/               # 웹 프론트엔드
├── data/                   # 데이터 디렉토리
│   ├── cache/              # 캐시 저장소
│   └── logs/               # 로그 파일
└── requirements.txt        # Python 의존성
```

## 🔧 Phase 2 구현 기능

### ✅ Web Search Tool
- DuckDuckGo API 웹 검색
- 웹 페이지 내용 추출 및 파싱
- URL 유효성 검증
- RSS/Atom 피드 파싱
- 뉴스 및 이미지 검색 지원
- 검색 캐싱 및 최적화
- 보안 도메인 필터링

### ✅ File System Tool
- 파일 읽기/쓰기 작업
- 디렉토리 생성 및 조회
- 파일 복사/이동/삭제
- 파일 검색 및 정보 조회
- 파일 모니터링 (watchdog)
- 백업/복원 기능
- 해시 계산 및 권한 관리

### ✅ Agent 서비스
- Function Calling 지원
- 도구 실행 관리
- 세션 및 컨텍스트 관리
- 도구 체이닝
- 통계 및 모니터링

### ✅ 보안 기능
- 안전 모드 (safe_mode)
- 허용 경로 제한
- 파일 확장자 검증
- 파일 크기 제한
- 디렉토리 탐색 공격 방지

## 🔧 Phase 1 구현 기능

### ✅ GPT API 연동
- OpenAI API 키 보안 관리
- tiktoken 기반 토큰 계산
- aiohttp 비동기 호출
- 재시도 로직 및 에러 핸들링

### ✅ 캐싱 시스템
- diskcache 기반 응답 캐시
- 설정 가능한 TTL
- 캐시 통계 및 관리

### ✅ 웹 인터페이스
- 실시간 채팅 UI
- 스트리밍 응답 지원
- 시스템 모니터링 대시보드
- 설정 관리

### ✅ API 엔드포인트
- `/api/chat/completion` - 채팅 완료
- `/api/chat/stream` - 스트리밍 채팅
- `/api/chat/conversation` - 대화 관리
- `/api/system/health` - 시스템 상태
- `/api/system/cache/clear` - 캐시 관리
- `/api/agent/tools` - 도구 목록 조회
- `/api/agent/execute` - 도구 실행
- `/api/agent/chat` - AI 에이전트 대화 (도구 사용 가능)
- `/api/agent/file` - 파일 작업 단순화 인터페이스
- `/api/agent/search` - 웹 검색 단순화 인터페이스

## 🎛️ 설정 옵션

### OpenAI 설정
- `OPENAI_MODEL`: 사용할 GPT 모델
- `OPENAI_MAX_TOKENS`: 최대 토큰 수
- `OPENAI_TEMPERATURE`: 창의성 수준

### 캐시 설정
- `CACHE_TYPE`: 캐시 유형 (disk/redis)
- `CACHE_TTL`: 캐시 유지 시간
- `CACHE_MAX_SIZE`: 최대 캐시 크기

### API 설정
- `API_HOST`: 서버 호스트
- `API_PORT`: 서버 포트
- `MAX_REQUESTS_PER_MINUTE`: 분당 최대 요청 수

## 🔮 향후 개발 계획

### Phase 3: 시스템 통합 및 추가 도구
- Calculator Tool - 수학 계산 도구 ✅
- Web Search Tool - 웹 검색 도구 ✅
- System Command Tool - 시스템 명령 실행
- Database Tool - 데이터베이스 연동
- Scheduler Tool - 작업 스케줄링

### Phase 4: 고급 기능
- 스마트 캐싱
- 요청 최적화
- 오프라인 모드
- 음성 인터페이스

## 🔍 API 문서

서버 실행 후 다음 URL에서 API 문서 확인:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ 개발 가이드

### 새로운 서비스 추가
1. `backend/services/`에 서비스 클래스 생성
2. `backend/api/`에 API 라우터 생성
3. `backend/main.py`에 라우터 등록

### 새로운 모델 추가
1. `backend/models/`에 Pydantic 모델 정의
2. 서비스에서 모델 사용

### 캐시 전략 변경
1. `backend/core/cache_manager.py` 수정
2. Redis 사용시 docker-compose.yml 활용

## 🧪 테스트

```bash
# 기본 테스트 (구현 예정)
pytest tests/

# API 테스트
curl -X POST "http://localhost:8000/api/chat/completion" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

## 📊 모니터링

### 로그 확인
```bash
tail -f data/logs/app.log
```

### 시스템 상태 확인
```bash
curl http://localhost:8000/api/system/health
```

### 캐시 통계 확인
```bash
curl http://localhost:8000/api/system/cache/stats
```

## 🐳 Docker 배포 (향후 지원)

```bash
# Docker 이미지 빌드
docker build -t local-ai-agent .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env local-ai-agent
```

## 🤝 기여 가이드

1. 이슈 생성 및 논의
2. 피처 브랜치 생성
3. 코드 작성 및 테스트
4. Pull Request 생성

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조

## 🆘 문제 해결

### 일반적인 문제

1. **OpenAI API 키 오류**
   - `.env` 파일의 API 키 확인
   - API 키 권한 및 크레딧 확인

2. **캐시 오류**
   - `data/cache` 디렉토리 권한 확인
   - 디스크 공간 확인

3. **포트 충돌**
   - `.env`에서 `API_PORT` 변경
   - 다른 프로세스의 포트 사용 확인

### 로그 확인
```bash
# 실시간 로그 모니터링
tail -f data/logs/app.log

# 오류 로그만 확인
grep "ERROR" data/logs/app.log
```

## 📞 지원

- 이슈 트래커: GitHub Issues
- 문서: `/docs` 엔드포인트
- 시스템 상태: `/api/system/health`

---

🚀 **Local AI Agent로 AI 기반 자동화를 시작하세요!**
