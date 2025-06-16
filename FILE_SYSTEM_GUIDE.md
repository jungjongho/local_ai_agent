# File System Tool 사용 가이드

## 🚀 Phase 2 구현 완료

Phase 2의 핵심 기능인 **File System Tool**이 성공적으로 구현되었습니다!

### 📋 구현된 기능

#### 1. 파일 시스템 도구 (FileSystemTool)
- ✅ 파일 읽기/쓰기
- ✅ 디렉토리 생성/조회
- ✅ 파일 복사/이동/삭제
- ✅ 파일 검색
- ✅ 파일 정보 조회
- ✅ 파일 모니터링 (watchdog)
- ✅ 백업/복원 기능
- ✅ 해시 계산
- ✅ 권한 관리

#### 2. 보안 기능
- ✅ 안전 모드 (safe_mode)
- ✅ 허용 경로 제한 (allowed_paths)
- ✅ 파일 확장자 검증
- ✅ 파일 크기 제한
- ✅ 디렉토리 탐색 공격 방지

#### 3. Agent 서비스
- ✅ 도구 실행 관리
- ✅ 세션 관리
- ✅ Function Calling 지원
- ✅ 도구 체이닝
- ✅ 통계 및 모니터링

## 🔧 API 엔드포인트

### Agent 관련 엔드포인트
```
GET  /api/agent/tools           # 사용 가능한 도구 목록
POST /api/agent/execute         # 도구 직접 실행
POST /api/agent/chat           # AI 에이전트와 대화 (도구 사용 가능)
POST /api/agent/file           # 파일 작업 단순화 인터페이스
GET  /api/agent/sessions/{id}  # 세션 정보 조회
GET  /api/agent/statistics     # 통계 정보
POST /api/agent/sessions/cleanup # 세션 정리
GET  /api/agent/health         # 헬스 체크
```

### 테스트 엔드포인트
```
POST /api/agent/test/file-read      # 파일 읽기 테스트
POST /api/agent/test/file-write     # 파일 쓰기 테스트
GET  /api/agent/test/directory-list # 디렉토리 조회 테스트
```

## 📝 사용 예제

### 1. 파일 읽기
```bash
curl -X POST "http://localhost:8000/api/agent/file" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "read",
    "path": "data/workspace/test_file.txt"
  }'
```

### 2. 파일 쓰기
```bash
curl -X POST "http://localhost:8000/api/agent/file" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "write",
    "path": "data/workspace/new_file.txt",
    "content": "Hello from AI Agent!"
  }'
```

### 3. 디렉토리 조회
```bash
curl -X POST "http://localhost:8000/api/agent/file" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "list",
    "path": "data/workspace",
    "recursive": false
  }'
```

### 4. 파일 검색
```bash
curl -X POST "http://localhost:8000/api/agent/file" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "search",
    "path": "data/workspace",
    "pattern": "*.txt",
    "recursive": true
  }'
```

### 5. AI 에이전트와 대화 (도구 사용)
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "workspace 폴더에 있는 파일들을 보여주세요"
      }
    ]
  }'
```

### 6. 도구 직접 실행
```bash
curl -X POST "http://localhost:8000/api/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "file_system",
    "parameters": {
      "operation": "info",
      "path": "data/workspace/test_file.txt"
    }
  }'
```

## 🔒 보안 설정

### 허용 경로
기본적으로 다음 경로만 접근 가능:
- `data/workspace/` - 작업 공간
- `data/temp/` - 임시 파일

### 허용 파일 확장자
```
.txt, .md, .json, .csv, .xml, .yml, .yaml,
.py, .js, .html, .css, .sql, .log
```

### 차단 파일 확장자
```
.exe, .bat, .cmd, .com, .scr, .vbs, .dll
```

### 파일 크기 제한
- 최대 파일 크기: 10MB
- 최대 디렉토리 깊이: 10레벨

## 📊 모니터링

### 도구 통계 확인
```bash
curl -X GET "http://localhost:8000/api/agent/statistics"
```

### 사용 가능한 도구 확인
```bash
curl -X GET "http://localhost:8000/api/agent/tools"
```

### 헬스 체크
```bash
curl -X GET "http://localhost:8000/api/agent/health"
```

## 🎯 고급 기능

### 1. 파일 모니터링
```json
{
  "operation": "watch",
  "path": "data/workspace"
}
```

### 2. 백업 생성
```json
{
  "operation": "backup",
  "path": "data/workspace/important_file.txt"
}
```

### 3. 해시 계산
```json
{
  "operation": "hash",
  "path": "data/workspace/test_file.txt",
  "algorithm": "sha256"
}
```

### 4. 권한 관리
```json
{
  "operation": "permissions",
  "path": "data/workspace/test_file.txt",
  "permissions": "644"
}
```

## 🧪 테스트 시나리오

### 시나리오 1: 기본 파일 작업
1. 파일 생성 및 내용 작성
2. 파일 읽기 및 내용 확인
3. 파일 정보 조회
4. 파일 백업 생성

### 시나리오 2: 디렉토리 관리
1. 새 디렉토리 생성
2. 파일들을 디렉토리로 이동
3. 디렉토리 내용 조회
4. 파일 검색

### 시나리오 3: AI 에이전트 상호작용
1. "workspace에 새 파일을 만들어주세요"
2. "방금 만든 파일의 내용을 보여주세요"
3. "workspace의 모든 파일을 찾아주세요"
4. "가장 큰 파일이 무엇인지 알려주세요"

## 🚧 다음 단계 (Phase 3)

File System Tool을 기반으로 다음 기능들을 추가할 예정:
- 📊 **Calculator Tool** - 수학 계산 도구
- 🌐 **Web Search Tool** - 웹 검색 도구  
- 💻 **System Command Tool** - 시스템 명령 실행
- 🗄️ **Database Tool** - 데이터베이스 연동
- 📅 **Scheduler Tool** - 작업 스케줄링

## 🎉 축하합니다!

Phase 2의 핵심 기능이 성공적으로 구현되었습니다. AI 에이전트가 이제 파일 시스템과 상호작용할 수 있으며, 안전하고 효율적인 파일 관리가 가능합니다.

파일 시스템 도구를 통해 AI 에이전트는:
- 📁 파일과 디렉토리를 관리할 수 있습니다
- 🔍 원하는 파일을 검색할 수 있습니다
- 💾 데이터를 안전하게 백업할 수 있습니다
- 👁️ 파일 변경사항을 모니터링할 수 있습니다
- 🔐 보안 정책에 따라 안전하게 작업할 수 있습니다

이제 AI 에이전트와 대화하며 파일 작업을 요청해보세요!
