from typing import Dict, Any, List, Optional
import json
from .base import EnhancedBaseAgent


class FrontendAgent(EnhancedBaseAgent):
    """Frontend 에이전트 - React 컴포넌트 및 페이지 코드 생성"""
    
    def __init__(self, model: Optional[str] = None):
        super().__init__(
            name="frontend",
            description="React + TypeScript + TailwindCSS 기반 프론트엔드 코드를 생성하는 에이전트",
            model=model
        )
    
    def get_system_prompt(self) -> str:
        return """당신은 전문 React 개발자 AI 에이전트입니다.

주어진 UI/UX 설계를 바탕으로 다음과 같은 작업을 수행해야 합니다:

1. React 컴포넌트 코드 생성
   - TypeScript 인터페이스 정의
   - Functional Component 구조
   - Props 타입 정의
   - TailwindCSS 스타일링

2. 페이지 컴포넌트 생성
   - 라우팅 구조
   - 상태 관리 (useState, useEffect)
   - API 호출 로직
   - 에러 처리

3. 서비스 함수 생성
   - Axios 기반 HTTP 클라이언트
   - API 엔드포인트 연동
   - 응답 데이터 타입 정의

4. 프로젝트 설정 파일
   - package.json
   - tsconfig.json
   - tailwind.config.js
   - vite.config.ts

모든 코드는 최신 React 18 + TypeScript + Vite 기준으로 작성하고,
Clean Code 원칙을 따라 읽기 쉽고 유지보수 가능한 코드를 생성하세요."""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Frontend 에이전트 실행"""
        try:
            requirements = input_data.get("requirements_analysis", {})
            design_system = input_data.get("design_system", {})
            components = input_data.get("components", [])
            layouts = input_data.get("layouts", [])
            navigation = input_data.get("navigation", {})
            
            # 1. 프로젝트 설정 파일 생성
            config_files = await self._generate_config_files(requirements)
            
            # 2. 공통 컴포넌트 생성
            common_components = await self._generate_common_components(components, design_system)
            
            # 3. 페이지 컴포넌트 생성
            page_components = await self._generate_page_components(layouts, requirements, design_system)
            
            # 4. 서비스 함수 생성
            services = await self._generate_services(requirements)
            
            # 5. 라우팅 설정 생성
            routing = await self._generate_routing(layouts, navigation)
            
            # 6. 메인 App 컴포넌트 생성
            app_component = await self._generate_app_component(navigation, design_system)
            
            return {
                "config_files": config_files,
                "components": common_components,
                "pages": page_components,
                "services": services,
                "routing": routing,
                "app_component": app_component,
                "next_agent": "backend"
            }
            
        except Exception as e:
            raise Exception(f"Frontend 에이전트 실행 실패: {str(e)}")
    
    async def _generate_config_files(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """프로젝트 설정 파일들 생성"""
        project_name = requirements.get("project_name", "react-app")
        
        # package.json
        package_json = {
            "name": project_name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0",
                "axios": "^1.3.0",
                "@headlessui/react": "^1.7.0",
                "@heroicons/react": "^2.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.0.27",
                "@types/react-dom": "^18.0.10",
                "@typescript-eslint/eslint-plugin": "^5.57.1",
                "@typescript-eslint/parser": "^5.57.1",
                "@vitejs/plugin-react": "^4.0.0",
                "autoprefixer": "^10.4.14",
                "eslint": "^8.38.0",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.3.4",
                "postcss": "^8.4.24",
                "tailwindcss": "^3.3.0",
                "typescript": "^5.0.2",
                "vite": "^4.3.2"
            }
        }
        
        # tsconfig.json
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "useDefineForClassFields": True,
                "lib": ["ES2020", "DOM", "DOM.Iterable"],
                "module": "ESNext",
                "skipLibCheck": True,
                "moduleResolution": "bundler",
                "allowImportingTsExtensions": True,
                "resolveJsonModule": True,
                "isolatedModules": True,
                "noEmit": True,
                "jsx": "react-jsx",
                "strict": True,
                "noUnusedLocals": True,
                "noUnusedParameters": True,
                "noFallthroughCasesInSwitch": True
            },
            "include": ["src"],
            "references": [{"path": "./tsconfig.node.json"}]
        }
        
        # tailwind.config.js
        tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}"""
        
        # vite.config.ts
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})"""
        
        return {
            "package.json": json.dumps(package_json, indent=2),
            "tsconfig.json": json.dumps(tsconfig, indent=2),
            "tailwind.config.js": tailwind_config,
            "vite.config.ts": vite_config,
            "postcss.config.js": """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}""",
            "src/index.css": """@tailwind base;
@tailwind components;
@tailwind utilities;"""
        }
    
    async def _generate_common_components(self, components: List[Dict[str, Any]], design_system: Dict[str, Any]) -> Dict[str, str]:
        """공통 컴포넌트 생성"""
        generated_components = {}
        
        for component in components:
            if component.get("type") == "common":
                component_code = await self._generate_single_component(component, design_system)
                generated_components[f"src/components/{component['name']}.tsx"] = component_code
        
        # 항상 포함되는 기본 컴포넌트들
        generated_components.update({
            "src/components/Button.tsx": self._get_button_component(),
            "src/components/Card.tsx": self._get_card_component(),
            "src/components/Loading.tsx": self._get_loading_component(),
            "src/components/ErrorMessage.tsx": self._get_error_component()
        })
        
        return generated_components
    
    async def _generate_single_component(self, component: Dict[str, Any], design_system: Dict[str, Any]) -> str:
        """단일 컴포넌트 코드 생성"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 컴포넌트를 React + TypeScript로 구현해주세요:

컴포넌트 정보:
{json.dumps(component, indent=2, ensure_ascii=False)}

디자인 시스템:
{json.dumps(design_system, indent=2)}

요구사항:
1. TypeScript 인터페이스 정의
2. Props 타입 정의
3. TailwindCSS 스타일링
4. 상태 관리 (필요시)
5. 에러 처리
6. JSDoc 주석

완전한 React 컴포넌트 코드를 생성해주세요.
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(messages, max_tokens=1500)
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_fallback_component(component["name"])
    
    async def _generate_page_components(self, layouts: List[Dict[str, Any]], requirements: Dict[str, Any], design_system: Dict[str, Any]) -> Dict[str, str]:
        """페이지 컴포넌트 생성"""
        generated_pages = {}
        api_endpoints = requirements.get("api_endpoints", [])
        
        for layout in layouts:
            page_code = await self._generate_single_page(layout, api_endpoints, design_system)
            page_name = layout["name"].replace(" ", "").replace("페이지", "Page")
            generated_pages[f"src/pages/{page_name}.tsx"] = page_code
        
        return generated_pages
    
    async def _generate_single_page(self, layout: Dict[str, Any], api_endpoints: List[Dict[str, Any]], design_system: Dict[str, Any]) -> str:
        """단일 페이지 컴포넌트 생성"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 페이지를 React + TypeScript로 구현해주세요:

페이지 정보:
{json.dumps(layout, indent=2, ensure_ascii=False)}

API 엔드포인트:
{json.dumps(api_endpoints, indent=2, ensure_ascii=False)}

디자인 시스템:
{json.dumps(design_system, indent=2)}

요구사항:
1. React Hooks (useState, useEffect) 사용
2. API 호출 로직 포함
3. 로딩/에러 상태 처리
4. 반응형 디자인
5. TypeScript 타입 정의
6. TailwindCSS 스타일링

완전한 React 페이지 컴포넌트를 생성해주세요.
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(messages, max_tokens=2000)
        
        if result["success"]:
            return result["content"]
        else:
            return self._get_fallback_page(layout["name"])
    
    async def _generate_services(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """서비스 함수 생성"""
        api_endpoints = requirements.get("api_endpoints", [])
        data_models = requirements.get("data_models", [])
        
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": f"""
다음 API 엔드포인트들에 대한 서비스 함수들을 생성해주세요:

API 엔드포인트:
{json.dumps(api_endpoints, indent=2, ensure_ascii=False)}

데이터 모델:
{json.dumps(data_models, indent=2, ensure_ascii=False)}

요구사항:
1. Axios 기반 HTTP 클라이언트
2. TypeScript 타입 정의
3. 에러 처리
4. 응답 데이터 타입 정의
5. API 기본 URL 설정

api.ts 파일 하나로 모든 API 호출 함수를 포함해주세요.
"""}
        ]
        
        result = await self.call_gpt_with_enhancements(messages, max_tokens=1500)
        
        if result["success"]:
            return {"src/services/api.ts": result["content"]}
        else:
            return {"src/services/api.ts": self._get_fallback_api_service()}
    
    async def _generate_routing(self, layouts: List[Dict[str, Any]], navigation: Dict[str, Any]) -> str:
        """라우팅 설정 생성"""
        routes = []
        for layout in layouts:
            page_name = layout["name"].replace(" ", "").replace("페이지", "Page")
            routes.append({
                "path": layout.get("path", "/"),
                "component": page_name
            })
        
        # 개별 import 문들 생성
        import_statements = []
        for route in routes:
            import_statements.append(f"import {route['component']} from '../pages/{route['component']}';")
        
        # Route 엘리먼트들 생성
        route_elements = []
        for route in routes:
            route_elements.append(f"        <Route path=\"{route['path']}\" element={{<{route['component']} />}} />")
        
        routing_code = f"""import {{ BrowserRouter as Router, Routes, Route }} from 'react-router-dom';
{chr(10).join(import_statements)}

const AppRoutes = () => {{
  return (
    <Router>
      <Routes>
{chr(10).join(route_elements)}
      </Routes>
    </Router>
  );
}};

export default AppRoutes;"""
        
        return routing_code
    
    async def _generate_app_component(self, navigation: Dict[str, Any], design_system: Dict[str, Any]) -> str:
        """메인 App 컴포넌트 생성"""
        return """import React from 'react';
import './index.css';
import AppRoutes from './routes/AppRoutes';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <AppRoutes />
    </div>
  );
}

export default App;"""
    
    def _get_button_component(self) -> str:
        """기본 Button 컴포넌트"""
        return """import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className = '',
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variantClasses = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const disabledClasses = 'opacity-50 cursor-not-allowed';
  
  const classes = [
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    disabled || loading ? disabledClasses : '',
    className,
  ].join(' ');
  
  return (
    <button
      type={type}
      className={classes}
      onClick={onClick}
      disabled={disabled || loading}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};

export default Button;"""
    
    def _get_card_component(self) -> str:
        """기본 Card 컴포넌트"""
        return """import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
}

const Card: React.FC<CardProps> = ({
  children,
  title,
  className = '',
  padding = 'md',
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };
  
  const classes = [
    'bg-white rounded-lg shadow-md border border-gray-200',
    paddingClasses[padding],
    className,
  ].join(' ');
  
  return (
    <div className={classes}>
      {title && (
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};

export default Card;"""
    
    def _get_loading_component(self) -> str:
        """기본 Loading 컴포넌트"""
        return """import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  text?: string;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'md',
  text = '로딩 중...',
}) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-8">
      <svg
        className={`animate-spin ${sizeClasses[size]} text-blue-600`}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      {text && <p className="mt-2 text-sm text-gray-600">{text}</p>}
    </div>
  );
};

export default Loading;"""
    
    def _get_error_component(self) -> str:
        """기본 ErrorMessage 컴포넌트"""
        return """import React from 'react';

interface ErrorMessageProps {
  message: string;
  title?: string;
  onRetry?: () => void;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  title = '오류가 발생했습니다',
  onRetry,
}) => {
  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-4">
      <div className="flex">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-red-400"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-800">{title}</h3>
          <p className="mt-1 text-sm text-red-700">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-sm text-red-800 underline hover:text-red-900"
            >
              다시 시도
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;"""
    
    def _get_fallback_component(self, name: str) -> str:
        """기본 컴포넌트 템플릿"""
        return f"""import React from 'react';

interface {name}Props {{
  // Props 정의
}}

const {name}: React.FC<{name}Props> = () => {{
  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold">{name} Component</h2>
      <p className="text-gray-600">이 컴포넌트는 자동 생성되었습니다.</p>
    </div>
  );
}};

export default {name};"""
    
    def _get_fallback_page(self, name: str) -> str:
        """기본 페이지 템플릿"""
        page_name = name.replace(" ", "").replace("페이지", "Page")
        return f"""import React from 'react';

const {page_name}: React.FC = () => {{
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">{name}</h1>
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-gray-600">이 페이지는 자동 생성되었습니다.</p>
        </div>
      </div>
    </div>
  );
}};

export default {page_name};"""
    
    def _get_fallback_api_service(self) -> str:
        """기본 API 서비스"""
        return """import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 토큰 등 인증 정보 추가 가능
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;"""
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        required_fields = ["requirements_analysis", "design_system", "components"]
        
        for field in required_fields:
            if field not in input_data:
                return False
        
        return True
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """출력 데이터 검증"""
        required_fields = ["config_files", "components", "pages", "services", "app_component"]
        
        for field in required_fields:
            if field not in output_data:
                return False
        
        # 설정 파일 검증
        config_files = output_data.get("config_files", {})
        if "package.json" not in config_files:
            return False
        
        return True
