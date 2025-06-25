from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import openai
from datetime import datetime
import logging
import json
import asyncio
from ..core.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """모든 AI 에이전트의 기본 클래스"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
        self.temperature = 0.7
        self.max_tokens = 2000
        
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트 실행 - 각 에이전트가 구현해야 함"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """시스템 프롬프트 반환 - 각 에이전트가 구현해야 함"""
        pass
    
    async def call_gpt(self, messages: list, **kwargs) -> Dict[str, Any]:
        """GPT API 호출"""
        try:
            # 기본 파라미터 설정
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # JSON 모드 요청시
            if kwargs.get("response_format") == "json":
                params["response_format"] = {"type": "json_object"}
            
            start_time = datetime.now()
            
            response = self.client.chat.completions.create(**params)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            # JSON 응답 파싱 시도
            try:
                if kwargs.get("response_format") == "json":
                    parsed_content = json.loads(content)
                else:
                    parsed_content = content
            except json.JSONDecodeError:
                parsed_content = content
            
            return {
                "success": True,
                "content": parsed_content,
                "tokens_used": response.usage.total_tokens,
                "duration": duration,
                "model": response.model
            }
            
        except Exception as e:
            logger.error(f"GPT API 호출 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "tokens_used": 0,
                "duration": 0
            }
    
    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """입력 데이터 검증"""
        return True  # 기본적으로 통과, 각 에이전트에서 오버라이드
    
    async def validate_output(self, output_data: Dict[str, Any]) -> bool:
        """출력 데이터 검증"""
        return True  # 기본적으로 통과, 각 에이전트에서 오버라이드
    
    def create_error_response(self, error_message: str, error_type: str = "execution_error") -> Dict[str, Any]:
        """에러 응답 생성"""
        return {
            "success": False,
            "agent_name": self.name,
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
    
    def create_success_response(self, result: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """성공 응답 생성"""
        response = {
            "success": True,
            "agent_name": self.name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response
    
    async def log_execution(self, workflow_id: int, status: str, input_data: Dict[str, Any], 
                          output_data: Optional[Dict[str, Any]] = None, 
                          error_data: Optional[Dict[str, Any]] = None) -> None:
        """실행 로그 기록"""
        try:
            log_data = {
                "workflow_id": workflow_id,
                "agent_name": self.name,
                "status": status,
                "input_data": input_data,
                "output_data": output_data,
                "error_data": error_data,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Agent 실행 로그: {json.dumps(log_data, indent=2, ensure_ascii=False)}")
            
        except Exception as e:
            logger.error(f"로그 기록 실패: {e}")


class RetryMixin:
    """재시도 기능을 제공하는 믹스인"""
    
    async def execute_with_retry(self, func, max_retries: int = 3, **kwargs):
        """함수를 재시도와 함께 실행"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await func(**kwargs)
            except Exception as e:
                last_error = e
                logger.warning(f"실행 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    # 지수 백오프로 대기
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
        
        raise last_error


class ValidationMixin:
    """검증 기능을 제공하는 믹스인"""
    
    def validate_json_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """JSON 스키마 검증"""
        try:
            # 간단한 스키마 검증 (실제로는 jsonschema 라이브러리 사용 권장)
            required_fields = schema.get("required", [])
            
            for field in required_fields:
                if field not in data:
                    logger.error(f"필수 필드 누락: {field}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"스키마 검증 실패: {e}")
            return False
    
    def validate_file_structure(self, structure: Dict[str, str]) -> bool:
        """파일 구조 검증"""
        try:
            for file_path, content in structure.items():
                # 파일 경로 검증
                if not file_path or ".." in file_path:
                    logger.error(f"잘못된 파일 경로: {file_path}")
                    return False
                
                # 내용 검증
                if not isinstance(content, str):
                    logger.error(f"잘못된 파일 내용 타입: {file_path}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"파일 구조 검증 실패: {e}")
            return False


class CacheMixin:
    """캐시 기능을 제공하는 믹스인"""
    
    def __init__(self):
        self._cache = {}
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        import hashlib
        content = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(content.encode()).hexdigest()
    
    async def cached_gpt_call(self, messages: list, **kwargs) -> Dict[str, Any]:
        """캐시된 GPT 호출"""
        cache_key = self.get_cache_key(messages, **kwargs)
        
        if cache_key in self._cache:
            logger.info(f"캐시 히트: {cache_key}")
            return self._cache[cache_key]
        
        result = await self.call_gpt(messages, **kwargs)
        
        if result["success"]:
            self._cache[cache_key] = result
            logger.info(f"캐시 저장: {cache_key}")
        
        return result
    
    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        logger.info("캐시가 초기화되었습니다.")


class EnhancedBaseAgent(BaseAgent, RetryMixin, ValidationMixin, CacheMixin):
    """향상된 기능을 포함한 기본 에이전트 클래스"""
    
    def __init__(self, name: str, description: str, enable_cache: bool = True):
        BaseAgent.__init__(self, name, description)
        if enable_cache:
            CacheMixin.__init__(self)
        
        self.enable_cache = enable_cache
        self.enable_retry = True
        self.max_retries = 3
    
    async def safe_execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """안전한 실행 (검증, 재시도, 로깅 포함)"""
        workflow_id = input_data.get("workflow_id", 0)
        
        try:
            # 1. 입력 검증
            if not await self.validate_input(input_data):
                return self.create_error_response("입력 데이터 검증 실패", "validation_error")
            
            # 2. 실행 시작 로그
            await self.log_execution(workflow_id, "started", input_data)
            
            # 3. 재시도와 함께 실행
            if self.enable_retry:
                result = await self.execute_with_retry(
                    self.execute, 
                    max_retries=self.max_retries,
                    input_data=input_data
                )
            else:
                result = await self.execute(input_data)
            
            # 4. 출력 검증
            if not await self.validate_output(result):
                return self.create_error_response("출력 데이터 검증 실패", "validation_error")
            
            # 5. 성공 로그
            await self.log_execution(workflow_id, "completed", input_data, result)
            
            return self.create_success_response(result)
            
        except Exception as e:
            # 6. 실패 로그
            error_data = {"error": str(e), "type": type(e).__name__}
            await self.log_execution(workflow_id, "failed", input_data, error_data=error_data)
            
            return self.create_error_response(str(e), "execution_error")
    
    async def call_gpt_with_enhancements(self, messages: list, **kwargs) -> Dict[str, Any]:
        """향상된 GPT 호출 (캐시, 재시도 등)"""
        if self.enable_cache:
            return await self.cached_gpt_call(messages, **kwargs)
        else:
            return await self.call_gpt(messages, **kwargs)
