from typing import Dict, Any
import json
import re
from datetime import datetime
from .base import EnhancedBaseAgent
from ..models.schemas import RequirementAnalysis, ProjectPlan


class PMAgent(EnhancedBaseAgent):
    """프로젝트 매니저 에이전트 - 요구사항 분석 및 프로젝트 계획 수립"""
    
    def __init__(self):
        super().__init__(
            name="pm",
            description="사용자 요구사항을 분석하고 프로젝트 계획을 수립하는 PM 에이전트"
        )
    
    def get_system_prompt(self) -> str:
        return """당신은 전문 프로젝트 매니저 AI 에이전트입니다.

사용자의 요구사항을 받아서 다음과 같은 작업을 수행해야 합니다:

1. 요구사항 분석
   - 프로젝트 타입 파악 (웹앱, 모바일앱, API 등)
   - 핵심 기능 추출
   - 기술적 요구사항 분석
   - UI/UX 요구사항 파악

2. 데이터 모델 설계
   - 필요한 데이터 엔티티 정의
   - 엔티티 간 관계 설정
   - 데이터베이스 스키마 제안

3. API 엔드포인트 설계
   - RESTful API 엔드포인트 정의
   - HTTP 메서드 및 경로 설정
   - 요청/응답 데이터 구조 정의

4. 기술 스택 추천
   - Frontend: React + TypeScript + TailwindCSS
   - Backend: FastAPI + SQLAlchemy + SQLite
   - 기타 필요한 라이브러리 추천

5. 프로젝트 복잡도 평가
   - simple: 기본 CRUD 기능만 있는 간단한 앱
   - medium: 여러 기능과 약간의 비즈니스 로직이 있는 앱
   - complex: 복잡한 비즈니스 로직, 실시간 기능, 고급 기능이 있는 앱

반드시 JSON 형태로 응답하고, 모든 필드를 포함해야 합니다."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """PM 에이전트 실행"""
        try:
            user_input = input_data.get("user_input", "")
            project_name = input_data.get("project_name", "")
            
            if not user_input:
                raise ValueError("사용자 입력이 필요합니다.")
            
            # 프로젝트 이름 자동 생성
            if not project_name:
                project_name = await self._generate_project_name(user_input)
            
            # GPT를 이용한 요구사항 분석
            analysis_result = await self._analyze_requirements(user_input)
            
            # 프로젝트 계획 생성
            project_plan = await self._create_project_plan(project_name, user_input, analysis_result)
            
            return {
                "project_name": project_name,
                "requirements_analysis": analysis_result,
                "project_plan": project_plan,
                "next_agent": "uiux"
            }
            
        except Exception as e:
            raise Exception(f"PM 에이전트 실행 실패: {str(e)}")
    
    async def _generate_project_name(self, user_input: str) -> str:
        """사용자 입력으로부터 프로젝트 이름 생성"""
        try:
            messages = [
                {"role": "system", "content": "사용자 입력을 바탕으로 영어로 간단한 프로젝트 이름을 생성하세요. 소문자와 하이픈만 사용하고, 10글자 이내로 만드세요."},
                {"role": "user", "content": f"다음 요구사항에 적합한 프로젝트 이름을 생성해주세요: {user_input}"}
            ]
            
            result = await self.call_gpt_with_enhancements(messages, max_tokens=50)
            
            if result["success"]:
                project_name = result["content"].strip().lower()
                # 특수문자 제거 및 하이픈으로 치환
                project_name = re.sub(r'[^a-z0-9\-]', '-', project_name)
                project_name = re.sub(r'-+', '-', project_name).strip('-')
                return project_name[:20]  # 최대 20글자
            else:
                # 기본 이름 생성
                timestamp = datetime.now().strftime("%m%d")
                return f"web-app-{timestamp}"
                
        except Exception:
            timestamp = datetime.now().strftime("%m%d")
            return f"web-app-{timestamp}"
    
    async def _analyze_requirements(self, user_input: str) -> Dict[str, Any]:
        """요구사항 분석"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 사용자 요구사항을 분석해주세요:

{user_input}

다음 JSON 형태로 응답해주세요:
{{
    "project_type": "웹앱 타입 (web_app, mobile_app, api_service 등)",
    "main_features": ["핵심 기능1", "핵심 기능2", "핵심 기능3"],
    "technical_requirements": ["기술적 요구사항1", "기술적 요구사항2"],
    "ui_requirements": ["UI/UX 요구사항1", "UI/UX 요구사항2"],
    "data_models": [
        {{
            "name": "모델명",
            "fields": [
                {{"name": "필드명", "type": "타입", "description": "설명"}}
            ],
            "relationships": ["관계 설명"]
        }}
    ],
    "api_endpoints": [
        {{
            "path": "/api/path",
            "method": "GET|POST|PUT|DELETE",
            "description": "엔드포인트 설명",
            "request_body": {{}},
            "response_body": {{}}
        }}
    ]
}}
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(
            messages, 
            response_format="json",
            max_tokens=2000
        )
        
        if result["success"]:
            return result["content"]
        else:
            raise Exception(f"요구사항 분석 실패: {result.get('error', 'Unknown error')}")
    
    async def _create_project_plan(self, project_name: str, user_input: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """프로젝트 계획 생성"""
        
        # 복잡도 평가
        complexity = self._evaluate_complexity(analysis)
        
        # 기술 스택 정의
        tech_stack = {
            "frontend": "React + TypeScript + TailwindCSS + Vite",
            "backend": "FastAPI + SQLAlchemy + SQLite",
            "ui_library": "Headless UI + Heroicons",
            "state_management": "React Hooks",
            "http_client": "Axios",
            "validation": "Pydantic",
            "deployment": "Docker + Docker Compose"
        }
        
        # 예상 시간 계산
        estimated_time = self._estimate_time(complexity)
        
        return {
            "project_name": project_name,
            "description": self._generate_description(user_input, analysis),
            "tech_stack": tech_stack,
            "requirements": analysis,
            "estimated_complexity": complexity,
            "estimated_time": estimated_time,
            "development_phases": [
                "UI/UX 설계",
                "Frontend 컴포넌트 개발",
                "Backend API 개발",
                "데이터베이스 설계",
                "DevOps 설정"
            ]
        }
    
    def _evaluate_complexity(self, analysis: Dict[str, Any]) -> str:
        """프로젝트 복잡도 평가"""
        main_features = analysis.get("main_features", [])
        data_models = analysis.get("data_models", [])
        api_endpoints = analysis.get("api_endpoints", [])
        
        # 점수 계산
        score = 0
        score += len(main_features) * 2
        score += len(data_models) * 3
        score += len(api_endpoints) * 1
        
        # 복잡한 키워드 감지
        complex_keywords = [
            "실시간", "채팅", "알림", "결제", "인증", "권한", "파일업로드", 
            "이메일", "소셜로그인", "검색", "필터링", "대시보드", "차트"
        ]
        
        text_content = str(analysis).lower()
        for keyword in complex_keywords:
            if keyword in text_content:
                score += 5
        
        if score <= 10:
            return "simple"
        elif score <= 25:
            return "medium"
        else:
            return "complex"
    
    def _estimate_time(self, complexity: str) -> str:
        """개발 시간 추정"""
        time_map = {
            "simple": "2-3시간",
            "medium": "4-6시간", 
            "complex": "1-2일"
        }
        return time_map.get(complexity, "4-6시간")
    
    def _generate_description(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """프로젝트 설명 생성"""
        main_features = analysis.get("main_features", [])
        features_text = ", ".join(main_features[:3])
        
        return f"{analysis.get('project_type', '웹 애플리케이션')} - {features_text} 등의 기능을 포함합니다."
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        required_fields = ["user_input"]
        
        for field in required_fields:
            if field not in input_data:
                return False
        
        user_input = input_data.get("user_input", "")
        if not user_input or len(user_input.strip()) < 10:
            return False
        
        return True
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """출력 데이터 검증"""
        required_fields = ["project_name", "requirements_analysis", "project_plan"]
        
        for field in required_fields:
            if field not in output_data:
                return False
        
        # 프로젝트 계획 필수 필드 검증
        project_plan = output_data.get("project_plan", {})
        plan_required_fields = ["tech_stack", "estimated_complexity"]
        
        for field in plan_required_fields:
            if field not in project_plan:
                return False
        
        return True
