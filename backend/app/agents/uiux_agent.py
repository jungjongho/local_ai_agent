from typing import Dict, Any, List
import json
from .base import EnhancedBaseAgent


class UIUXAgent(EnhancedBaseAgent):
    """UI/UX 에이전트 - 컴포넌트 설계 및 디자인 시스템 구축"""
    
    def __init__(self):
        super().__init__(
            name="uiux",
            description="UI/UX 설계 및 컴포넌트 디자인을 담당하는 에이전트"
        )
    
    def get_system_prompt(self) -> str:
        return """당신은 전문 UI/UX 디자이너 AI 에이전트입니다.

주어진 요구사항을 바탕으로 다음과 같은 작업을 수행해야 합니다:

1. 디자인 시스템 설계
   - 컬러 팔레트 정의
   - 타이포그래피 설정
   - 스페이싱 시스템
   - 컴포넌트 스타일 가이드

2. React 컴포넌트 구조 설계
   - 재사용 가능한 컴포넌트 식별
   - 컴포넌트 계층 구조 설계
   - Props 인터페이스 정의
   - TailwindCSS 클래스 활용

3. 페이지 레이아웃 설계
   - 와이어프레임 구조
   - 네비게이션 설계
   - 반응형 레이아웃
   - 사용자 플로우

4. 인터랙션 설계
   - 버튼 및 폼 인터랙션
   - 로딩 상태 처리
   - 에러 메시지 표시
   - 성공 알림

모든 응답은 JSON 형태로 하고, TailwindCSS 클래스만 사용하세요.
현대적이고 깔끔한 디자인을 추구하며, 사용자 경험을 최우선으로 고려하세요."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """UI/UX 에이전트 실행"""
        try:
            requirements = input_data.get("requirements_analysis", {})
            project_plan = input_data.get("project_plan", {})
            
            # 1. 디자인 시스템 생성
            design_system = await self._create_design_system(requirements)
            
            # 2. 컴포넌트 설계
            components = await self._design_components(requirements, design_system)
            
            # 3. 페이지 레이아웃 설계
            layouts = await self._design_layouts(requirements, components)
            
            # 4. 네비게이션 설계
            navigation = await self._design_navigation(requirements)
            
            return {
                "design_system": design_system,
                "components": components,
                "layouts": layouts,
                "navigation": navigation,
                "next_agent": "frontend"
            }
            
        except Exception as e:
            raise Exception(f"UI/UX 에이전트 실행 실패: {str(e)}")
    
    async def _create_design_system(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """디자인 시스템 생성"""
        project_type = requirements.get("project_type", "web_app")
        main_features = requirements.get("main_features", [])
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
프로젝트 타입: {project_type}
주요 기능: {', '.join(main_features)}

이 프로젝트에 적합한 디자인 시스템을 설계해주세요.

다음 JSON 형태로 응답해주세요:
{{
    "colors": {{
        "primary": "blue-600",
        "secondary": "gray-600",
        "accent": "purple-500",
        "background": "gray-50",
        "surface": "white",
        "text": {{
            "primary": "gray-900",
            "secondary": "gray-600",
            "muted": "gray-400"
        }},
        "border": "gray-200",
        "success": "green-500",
        "warning": "yellow-500",
        "error": "red-500"
    }},
    "typography": {{
        "fontFamily": "font-sans",
        "sizes": {{
            "xs": "text-xs",
            "sm": "text-sm",
            "base": "text-base",
            "lg": "text-lg",
            "xl": "text-xl",
            "2xl": "text-2xl",
            "3xl": "text-3xl"
        }}
    }},
    "spacing": {{
        "xs": "p-1",
        "sm": "p-2",
        "md": "p-4",
        "lg": "p-6",
        "xl": "p-8"
    }},
    "borders": {{
        "radius": {{
            "sm": "rounded-sm",
            "md": "rounded-md",
            "lg": "rounded-lg"
        }},
        "width": "border"
    }},
    "shadows": {{
        "sm": "shadow-sm",
        "md": "shadow-md",
        "lg": "shadow-lg"
    }}
}}
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(
            messages, 
            response_format="json",
            max_tokens=1000
        )
        
        if result["success"]:
            return result["content"]
        else:
            # 기본 디자인 시스템 반환
            return self._get_default_design_system()
    
    async def _design_components(self, requirements: Dict[str, Any], design_system: Dict[str, Any]) -> List[Dict[str, Any]]:
        """컴포넌트 설계"""
        main_features = requirements.get("main_features", [])
        data_models = requirements.get("data_models", [])
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
주요 기능: {', '.join(main_features)}
데이터 모델: {json.dumps(data_models, indent=2, ensure_ascii=False)}
디자인 시스템: {json.dumps(design_system, indent=2)}

이 프로젝트에 필요한 React 컴포넌트들을 설계해주세요.

다음 JSON 형태로 응답해주세요:
[
    {{
        "name": "컴포넌트명",
        "type": "common|feature|layout",
        "description": "컴포넌트 설명",
        "props": [
            {{
                "name": "props명",
                "type": "string|number|boolean|object|array",
                "required": true,
                "description": "props 설명"
            }}
        ],
        "styling": {{
            "container": "TailwindCSS 클래스들",
            "elements": {{
                "title": "TailwindCSS 클래스들",
                "content": "TailwindCSS 클래스들",
                "button": "TailwindCSS 클래스들"
            }}
        }},
        "functionality": "컴포넌트 주요 기능 설명",
        "states": ["normal", "loading", "error", "success"]
    }}
]
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
            return self._get_default_components()
    
    async def _design_layouts(self, requirements: Dict[str, Any], components: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """페이지 레이아웃 설계"""
        main_features = requirements.get("main_features", [])
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
주요 기능: {', '.join(main_features)}
사용 가능한 컴포넌트: {json.dumps([c["name"] for c in components], ensure_ascii=False)}

이 프로젝트에 필요한 페이지 레이아웃들을 설계해주세요.

다음 JSON 형태로 응답해주세요:
[
    {{
        "name": "페이지명",
        "path": "/url-path",
        "description": "페이지 설명",
        "layout": {{
            "type": "single-column|two-column|grid",
            "header": {{
                "components": ["Header"],
                "styling": "TailwindCSS 클래스들"
            }},
            "main": {{
                "components": ["컴포넌트명1", "컴포넌트명2"],
                "styling": "TailwindCSS 클래스들",
                "grid": "grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
            }},
            "sidebar": {{
                "components": ["Sidebar"],
                "styling": "TailwindCSS 클래스들"
            }},
            "footer": {{
                "components": ["Footer"],
                "styling": "TailwindCSS 클래스들"
            }}
        }},
        "responsive": {{
            "mobile": "TailwindCSS 모바일 클래스들",
            "tablet": "TailwindCSS 태블릿 클래스들",
            "desktop": "TailwindCSS 데스크탑 클래스들"
        }}
    }}
]
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(
            messages, 
            response_format="json",
            max_tokens=1500
        )
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_default_layouts()
    
    async def _design_navigation(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """네비게이션 설계"""
        main_features = requirements.get("main_features", [])
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
주요 기능: {', '.join(main_features)}

이 프로젝트에 적합한 네비게이션을 설계해주세요.

다음 JSON 형태로 응답해주세요:
{{
    "type": "horizontal|vertical|sidebar",
    "structure": [
        {{
            "label": "메뉴명",
            "path": "/url-path",
            "icon": "아이콘명",
            "children": [
                {{
                    "label": "서브메뉴명",
                    "path": "/sub-path"
                }}
            ]
        }}
    ],
    "styling": {{
        "container": "TailwindCSS 클래스들",
        "item": "TailwindCSS 클래스들",
        "active": "TailwindCSS 활성 상태 클래스들",
        "hover": "TailwindCSS 호버 상태 클래스들"
    }},
    "responsive": {{
        "mobile": "모바일에서는 햄버거 메뉴",
        "desktop": "데스크탑에서는 전체 메뉴 표시"
    }}
}}
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(
            messages, 
            response_format="json",
            max_tokens=1000
        )
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_default_navigation()
    
    def _get_default_design_system(self) -> Dict[str, Any]:
        """기본 디자인 시스템"""
        return {
            "colors": {
                "primary": "blue-600",
                "secondary": "gray-600",
                "accent": "purple-500",
                "background": "gray-50",
                "surface": "white",
                "text": {
                    "primary": "gray-900",
                    "secondary": "gray-600",
                    "muted": "gray-400"
                },
                "border": "gray-200",
                "success": "green-500",
                "warning": "yellow-500",
                "error": "red-500"
            },
            "typography": {
                "fontFamily": "font-sans",
                "sizes": {
                    "xs": "text-xs",
                    "sm": "text-sm",
                    "base": "text-base",
                    "lg": "text-lg",
                    "xl": "text-xl",
                    "2xl": "text-2xl",
                    "3xl": "text-3xl"
                }
            },
            "spacing": {
                "xs": "p-1",
                "sm": "p-2",
                "md": "p-4",
                "lg": "p-6",
                "xl": "p-8"
            },
            "borders": {
                "radius": {
                    "sm": "rounded-sm",
                    "md": "rounded-md",
                    "lg": "rounded-lg"
                },
                "width": "border"
            },
            "shadows": {
                "sm": "shadow-sm",
                "md": "shadow-md",
                "lg": "shadow-lg"
            }
        }
    
    def _get_default_components(self) -> List[Dict[str, Any]]:
        """기본 컴포넌트 목록"""
        return [
            {
                "name": "Button",
                "type": "common",
                "description": "재사용 가능한 버튼 컴포넌트",
                "props": [
                    {"name": "children", "type": "string", "required": True, "description": "버튼 텍스트"},
                    {"name": "variant", "type": "string", "required": False, "description": "버튼 스타일 변형"},
                    {"name": "onClick", "type": "function", "required": False, "description": "클릭 핸들러"}
                ],
                "styling": {
                    "container": "px-4 py-2 rounded-md font-medium transition-colors",
                    "variants": {
                        "primary": "bg-blue-600 text-white hover:bg-blue-700",
                        "secondary": "bg-gray-200 text-gray-900 hover:bg-gray-300"
                    }
                },
                "functionality": "클릭 이벤트 처리 및 스타일 변형",
                "states": ["normal", "hover", "disabled", "loading"]
            },
            {
                "name": "Card",
                "type": "common",
                "description": "콘텐츠를 담는 카드 컴포넌트",
                "props": [
                    {"name": "children", "type": "object", "required": True, "description": "카드 내용"},
                    {"name": "title", "type": "string", "required": False, "description": "카드 제목"}
                ],
                "styling": {
                    "container": "bg-white rounded-lg shadow-md p-6 border border-gray-200",
                    "title": "text-lg font-semibold text-gray-900 mb-4",
                    "content": "text-gray-600"
                },
                "functionality": "콘텐츠 그룹화 및 시각적 구분",
                "states": ["normal", "hover"]
            }
        ]
    
    def _get_default_layouts(self) -> List[Dict[str, Any]]:
        """기본 레이아웃 목록"""
        return [
            {
                "name": "홈페이지",
                "path": "/",
                "description": "메인 대시보드 페이지",
                "layout": {
                    "type": "single-column",
                    "header": {
                        "components": ["Header"],
                        "styling": "bg-white border-b border-gray-200"
                    },
                    "main": {
                        "components": ["Hero", "FeatureList"],
                        "styling": "container mx-auto px-4 py-8",
                        "grid": "space-y-8"
                    },
                    "footer": {
                        "components": ["Footer"],
                        "styling": "bg-gray-50 border-t border-gray-200"
                    }
                },
                "responsive": {
                    "mobile": "px-4",
                    "tablet": "px-6",
                    "desktop": "px-8"
                }
            }
        ]
    
    def _get_default_navigation(self) -> Dict[str, Any]:
        """기본 네비게이션"""
        return {
            "type": "horizontal",
            "structure": [
                {
                    "label": "홈",
                    "path": "/",
                    "icon": "home"
                },
                {
                    "label": "대시보드",
                    "path": "/dashboard",
                    "icon": "chart"
                }
            ],
            "styling": {
                "container": "bg-white border-b border-gray-200 px-4 py-3",
                "item": "text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium",
                "active": "text-blue-600 bg-blue-50",
                "hover": "bg-gray-50"
            },
            "responsive": {
                "mobile": "모바일에서는 햄버거 메뉴",
                "desktop": "데스크탑에서는 전체 메뉴 표시"
            }
        }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        required_fields = ["requirements_analysis", "project_plan"]
        
        for field in required_fields:
            if field not in input_data:
                return False
        
        requirements = input_data.get("requirements_analysis", {})
        if not requirements.get("main_features"):
            return False
        
        return True
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """출력 데이터 검증"""
        required_fields = ["design_system", "components", "layouts", "navigation"]
        
        for field in required_fields:
            if field not in output_data:
                return False
        
        # 컴포넌트 검증
        components = output_data.get("components", [])
        if not isinstance(components, list) or len(components) == 0:
            return False
        
        return True
