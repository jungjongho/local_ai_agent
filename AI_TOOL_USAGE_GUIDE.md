# AI 에이전트 도구 사용 가이드

## 🤖 AI가 직접 작업하도록 하는 방법

이제 AI 에이전트가 직접 파일을 생성하고 웹을 검색할 수 있습니다!

### ✅ 해결된 문제

**이전**: "죄송합니다, 제가 파일을 생성하거나 수정하는 기능은 없습니다..."
**현재**: AI가 직접 도구를 사용하여 작업을 수행합니다!

### 🔧 구현된 개선사항

1. **OpenAI Tools API 지원**: 최신 `tools`와 `tool_choice` 파라미터 사용
2. **자동 시스템 프롬프트**: AI에게 도구 사용을 적극 권장
3. **향상된 에러 처리**: 도구 호출 실패 시 적절한 대응
4. **캐싱 최적화**: 도구 호출 시에는 캐시 비활성화

### 🚀 사용 예시

#### 1. 파일 생성 요청
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "data/workspace 경로에 '안녕'이 적혀있는 hello.txt 파일을 만들어주세요"
      }
    ]
  }'
```

**AI 응답**: 
- ✅ file_system 도구를 사용하여 실제로 파일 생성
- 파일 생성 결과 확인 및 사용자에게 보고

#### 2. 웹 검색 요청
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Python 최신 뉴스를 검색해서 요약해주세요"
      }
    ]
  }'
```

**AI 응답**:
- ✅ web_search 도구를 사용하여 실제 검색 수행
- 검색 결과를 분석하고 요약 제공

#### 3. 복합 작업 요청
```bash
curl -X POST "http://localhost:8000/api/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "AI 뉴스를 검색해서 요약한 내용을 파일로 저장해주세요"
      }
    ]
  }'
```

**AI 응답**:
- ✅ web_search로 AI 뉴스 검색
- ✅ file_system으로 요약 내용을 파일에 저장
- 전체 과정과 결과 보고

### 🎯 지원되는 작업 유형

#### 파일 작업
- ✅ "파일을 만들어주세요"
- ✅ "파일 내용을 읽어주세요" 
- ✅ "파일을 복사해주세요"
- ✅ "폴더를 만들어주세요"
- ✅ "파일을 삭제해주세요"
- ✅ "파일 정보를 확인해주세요"

#### 웹 검색 작업
- ✅ "XXX에 대해 검색해주세요"
- ✅ "최신 뉴스를 찾아주세요"
- ✅ "이 웹사이트 내용을 요약해주세요"
- ✅ "URL이 접근 가능한지 확인해주세요"
- ✅ "RSS 피드를 분석해주세요"

#### 복합 작업
- ✅ "검색해서 파일로 저장해주세요"
- ✅ "파일을 읽고 웹에서 관련 정보를 찾아주세요"
- ✅ "여러 웹사이트를 분석해서 비교 보고서를 만들어주세요"

### 🔧 기술적 세부사항

#### Function Calling 설정
```python
# AI에게 제공되는 시스템 프롬프트
system_prompt = """You are a helpful AI assistant with access to the following tools:

- file_system: Comprehensive file system operations tool
- web_search: Web search and information gathering tool

When a user asks you to perform tasks that can be accomplished with these tools, 
you should use them actively rather than just explaining how they could do it themselves.

Be proactive in using tools to complete tasks for the user."""
```

#### 도구 호출 흐름
1. 사용자 요청 분석
2. 적절한 도구 선택
3. 도구 파라미터 생성
4. 도구 실행
5. 결과 분석 및 사용자에게 보고

#### 에러 처리
- 도구 실행 실패 시 사용자에게 명확한 설명
- 재시도 로직으로 일시적 오류 해결
- 대안 방법 제시

### 📊 성능 모니터링

#### 도구 사용 통계 확인
```bash
curl -X GET "http://localhost:8000/api/agent/statistics"
```

#### 세션 정보 확인
```bash
curl -X GET "http://localhost:8000/api/agent/sessions/{session_id}"
```

#### 헬스 체크
```bash
curl -X GET "http://localhost:8000/api/agent/health"
```

### 🛡️ 보안 및 제한사항

#### 파일 시스템 보안
- 허용된 경로만 접근 가능: `data/workspace`, `data/temp`
- 안전한 파일 확장자만 허용
- 파일 크기 제한: 10MB
- 자동 백업 생성

#### 웹 검색 보안
- 악성 도메인 자동 차단
- 콘텐츠 크기 제한: 50KB
- 요청 타임아웃: 30초
- 의심스러운 URL 패턴 차단

### 🚧 문제 해결

#### AI가 도구를 사용하지 않는 경우
1. OpenAI API 키 확인
2. 모델이 Function Calling을 지원하는지 확인 (gpt-3.5-turbo, gpt-4)
3. 로그에서 도구 호출 과정 확인
4. 요청이 명확하고 구체적인지 확인

#### 도구 실행 실패
1. 경로 권한 확인 (파일 시스템)
2. 네트워크 연결 확인 (웹 검색)
3. 로그 파일에서 상세 오류 확인: `data/logs/app.log`

### 🎉 사용 팁

#### 효과적인 요청 방법
1. **구체적으로 요청**: "파일을 만들어주세요" → "data/workspace에 hello.txt 파일을 만들어주세요"
2. **목적을 명시**: "검색해주세요" → "Python 튜토리얼을 검색해서 학습 계획을 세우는데 도움을 주세요"
3. **복합 작업 요청**: "검색해서 파일로 저장해주세요"

#### 자주 사용되는 패턴
- 📁 **파일 관리**: "워크스페이스를 정리해주세요"
- 🔍 **정보 수집**: "이 주제에 대해 조사해서 보고서를 만들어주세요"
- 💾 **데이터 저장**: "검색 결과를 정리해서 저장해주세요"

이제 AI 에이전트가 실제로 작업을 수행할 수 있습니다! 더 이상 "할 수 없습니다"라고 하지 않고, 직접 도구를 사용해서 사용자를 도와줍니다. 🚀
