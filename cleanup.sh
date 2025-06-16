#!/bin/bash
# 프로젝트 정리 - 백엔드 전용 구조로 변경

echo "🧹 프로젝트를 백엔드 전용 구조로 정리 중..."

# 프로젝트 루트의 불필요한 파일들 삭제
rm -f run_server.py
rm -f Makefile  
rm -f requirements.txt  # backend에 복사했으므로 삭제
rm -f run.sh
rm -f run.bat

echo "✅ 정리 완료!"
echo ""
echo "📁 현재 구조:"
echo "├── backend/          # 백엔드 메인 디렉토리"
echo "│   ├── main.py       # 서버 진입점"
echo "│   ├── requirements.txt"
echo "│   ├── setup.sh      # 설정 스크립트"
echo "│   └── ..."
echo "├── frontend/         # 리액트 프론트엔드 (별도 관리)"
echo "└── data/            # 데이터 저장소"
echo ""
echo "🚀 백엔드 실행 방법:"
echo "1. cd backend"
echo "2. source venv/bin/activate"
echo "3. bash setup.sh  # 최초 설정 시"
echo "4. python main.py"
