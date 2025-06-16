# Web Search Tool 사용 가이드

## 🌐 Web Search Tool 구현 완료

인터넷 검색 및 정보 수집을 위한 **Web Search Tool**이 성공적으로 구현되었습니다!

### 📋 구현된 기능

#### 1. 웹 검색 기능
- ✅ DuckDuckGo API 검색
- ✅ 다중 검색 엔진 지원 (Google Custom, Bing 확장 가능)
- ✅ 검색 결과 필터링 (시간 범위, 언어, 지역)
- ✅ 뉴스, 이미지 검색 지원
- ✅ 검색 캐싱 및 최적화

#### 2. 콘텐츠 추출 기능
- ✅ 웹 페이지 내용 추출
- ✅ HTML 파싱 및 정리
- ✅ 메타데이터 추출 (제목, 설명, 링크)
- ✅ 본문 내용 자동 식별
- ✅ 링크 및 이미지 정보 수집

#### 3. URL 유틸리티
- ✅ URL 접근성 검증
- ✅ HTTP 상태 및 헤더 정보
- ✅ RSS/Atom 피드 파싱
- ✅ 대량 URL 처리 (bulk operations)

#### 4. 보안 기능
- ✅ 허용/차단 도메인 관리
- ✅ 의심스러운 URL 패턴 차단
- ✅ 콘텐츠 크기 제한
- ✅ 요청 타임아웃 관리

## 🔧 API 엔드포인트

### 웹 검색 엔드포인트
```
POST /api/agent/search          # 웹 검색 작업
POST /api/agent/test/web-search # 웹 검색 테스트
POST /api/agent/test/extract-content # 콘텐츠 추출 테스트
POST /api/agent/test/validate-url    # URL 검증 테스트
```

## 📝 사용 예제

### 1. 일반 웹 검색
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "search",
    "query": "Python programming tutorial",
    "search_engine": "duckduckgo",
    "max_results": 10,
    "time_range": "week"
  }'
```

### 2. 웹 페이지 내용 추출
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "extract_content",
    "query": "https://en.wikipedia.org/wiki/Artificial_intelligence"
  }'
```

### 3. URL 유효성 검증
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "validate_url",
    "query": "https://www.example.com"
  }'
```

### 4. RSS 피드 파싱
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "parse_rss",
    "query": "https://feeds.bbci.co.uk/news/rss.xml"
  }'
```

### 5. 페이지 종합 정보
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "get_page_info",
    "query": "https://www.python.org"
  }'
```

### 6. AI 에이전트와 검색 대화
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

### 7. 뉴스 검색
```bash
curl -X POST "http://localhost:8000/api/agent/search" \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "search_news",
    "query": "artificial intelligence",
    "time_range": "week",
    "max_results": 5
  }'
```

## 🎯 지원되는 작업 (Operations)

### 검색 작업
- `search` - 일반 웹 검색
- `search_news` - 뉴스 검색
- `search_images` - 이미지 검색 (예정)

### 콘텐츠 작업
- `extract_content` - 웹 페이지 내용 추출
- `get_page_info` - 페이지 종합 정보
- `parse_rss` - RSS/Atom 피드 파싱

### 유틸리티 작업
- `validate_url` - URL 접근성 검증
- `bulk_search` - 대량 URL 처리

## 🔒 보안 설정

### 허용/차단 도메인
```python
# 기본 차단 도메인
blocked_domains = ["malware.com", "phishing.com", "spam.com"]

# 허용 도메인 (설정 시 이 도메인들만 허용)
allowed_domains = ["wikipedia.org", "python.org", "github.com"]
```

### 콘텐츠 제한
- 최대 콘텐츠 크기: 50KB
- 요청 타임아웃: 30초
- 최대 검색 결과: 50개

### 안전 기능
- JavaScript, VBScript 등 위험한 스키마 차단
- 로컬 IP 주소 접근 차단
- 의심스러운 URL 패턴 감지

## 📊 검색 엔진별 특징

### DuckDuckGo (기본)
- ✅ 무료 API 사용
- ✅ 프라이버시 보호
- ✅ 즉시 사용 가능
- ⚠️ 검색 결과 제한적

### Google Custom Search
- 🔑 API 키 필요
- ✅ 고품질 검색 결과
- ✅ 다양한 필터 옵션
- 💰 유료 서비스

### Bing Search
- 🔑 API 키 필요
- ✅ 이미지/뉴스 검색 지원
- ✅ 지역화된 결과
- 💰 유료 서비스

## 🧪 테스트 시나리오

### 시나리오 1: 기본 검색 및 추출
1. "Python tutorial" 검색
2. 첫 번째 결과 URL에서 내용 추출
3. 추출된 내용 요약

### 시나리오 2: 뉴스 수집
1. "AI news" 검색
2. RSS 피드 파싱
3. 최신 기사 목록 생성

### 시나리오 3: 웹사이트 분석
1. 웹사이트 URL 유효성 검증
2. 페이지 메타데이터 수집
3. 주요 링크 추출

### 시나리오 4: AI 에이전트 검색 대화
1. "최신 기술 트렌드를 검색해주세요"
2. "검색 결과를 바탕으로 요약해주세요"
3. "관련 링크들을 정리해주세요"

## 🔧 고급 기능

### 캐싱 시스템
```python
# 검색 결과 캐싱 (1시간)
cache_ttl = 3600
enable_caching = True
```

### 콘텐츠 필터링
```python
# HTML 태그 제거
# JavaScript/CSS 제거
# 본문 내용만 추출
# 링크 정보 별도 수집
```

### 비동기 처리
```python
# HTTP 세션 풀링
# 동시 요청 제한
# 타임아웃 관리
# 에러 핸들링
```

## ⚡ 성능 최적화

### 요청 최적화
- HTTP 연결 풀링
- 요청 간 지연 (0.5초)
- 콘텐츠 크기 제한
- 타임아웃 설정

### 캐싱 전략
- 검색 결과 캐싱
- 메모리 기반 빠른 접근
- TTL 기반 자동 만료
- 중복 요청 방지

## 🚧 확장 계획

### 추가 예정 기능
- 📊 **검색 분석**: 검색 트렌드 분석
- 🖼️ **이미지 검색**: 이미지 검색 및 분석
- 📄 **PDF 처리**: PDF 문서 내용 추출
- 🌍 **다국어 지원**: 자동 언어 감지 및 번역

### API 확장
- GraphQL 지원
- 웹훅 알림
- 실시간 검색
- 검색 히스토리

## 🎉 사용법 요약

이제 AI 에이전트가 인터넷을 검색하고 정보를 수집할 수 있습니다:

1. **웹 검색**: "Python tutorial을 검색해주세요"
2. **내용 추출**: "이 웹사이트의 내용을 요약해주세요"
3. **URL 검증**: "이 사이트가 접속 가능한지 확인해주세요"
4. **뉴스 수집**: "AI 관련 최신 뉴스를 찾아주세요"
5. **피드 분석**: "이 RSS 피드의 최신 글들을 보여주세요"

Web Search Tool을 통해 AI 에이전트의 정보 수집 능력이 대폭 향상되었습니다! 🚀
