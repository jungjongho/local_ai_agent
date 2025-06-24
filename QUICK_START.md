# 🚀 Local AI Agent 실행 가이드

## 빠른 시작

### 1️⃣ 환경 설정
```bash
# 프로젝트 디렉토리로 이동
cd backend

# Python 의존성 설치
pip install -r requirements.txt

# 환경 변수 파일 생성
cp .env.example .env
```

### 2️⃣ OpenAI API 키 설정
`.env` 파일을 열고 API 키를 설정하세요:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3️⃣ 서버 실행
```bash
# 백엔드 디렉토리에서
python main.py
```

### 4️⃣ 웹 인터페이스 접속
브라우저에서 다음 URL로 접속:
- **웹 UI**: http://localhost:8025/static/index.html
- **API 문서**: http://localhost:8025/docs

## ✅ 체크리스트

- [ ] Python 3.8+ 설치됨
- [ ] 의존성 설치 완료 (`pip install -r requirements.txt`)
- [ ] `.env` 파일에 OpenAI API 키 설정
- [ ] 서버 실행 (`python main.py`)
- [ ] 웹 브라우저에서 정상 접속 확인

## 🛠️ 문제 해결

### 포트 충돌 시
`.env` 파일에서 포트 변경:
```bash
API_PORT=8026  # 다른 포트로 변경
```

### 의존성 오류 시
```bash
# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows

# 의존성 재설치
pip install -r requirements.txt
```

### API 키 관련 오류
1. OpenAI 계정에서 API 키 발급
2. `.env` 파일에 정확히 입력
3. API 키에 크레딧이 있는지 확인

---

🎉 **설정 완료! Local AI Agent를 사용할 준비가 되었습니다.**
