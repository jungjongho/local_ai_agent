from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from ..core.config import settings

router = APIRouter()


@router.get("/models", response_model=Dict[str, Any])
async def get_available_models():
    """사용 가능한 GPT 모델 목록과 정보를 반환"""
    try:
        models_info = []
        
        for model in settings.AVAILABLE_MODELS:
            model_info = {
                "id": model,
                "name": model,
                "description": settings.MODEL_DESCRIPTIONS.get(model, "GPT 모델"),
                "use_cases": settings.MODEL_USE_CASES.get(model, []),
                "is_default": model == settings.DEFAULT_GPT_MODEL,
                "capabilities": _get_model_capabilities(model),
                "pricing_tier": _get_pricing_tier(model),
                "performance_tier": _get_performance_tier(model)
            }
            models_info.append(model_info)
        
        return {
            "success": True,
            "models": models_info,
            "default_model": settings.DEFAULT_GPT_MODEL,
            "total_count": len(models_info)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 정보 조회 실패: {str(e)}"
        )


@router.get("/models/{model_id}", response_model=Dict[str, Any])
async def get_model_info(model_id: str):
    """특정 모델의 상세 정보를 반환"""
    try:
        if model_id not in settings.AVAILABLE_MODELS:
            raise HTTPException(
                status_code=404,
                detail=f"모델을 찾을 수 없습니다: {model_id}"
            )
        
        model_info = {
            "id": model_id,
            "name": model_id,
            "description": settings.MODEL_DESCRIPTIONS.get(model_id, "GPT 모델"),
            "use_cases": settings.MODEL_USE_CASES.get(model_id, []),
            "is_default": model_id == settings.DEFAULT_GPT_MODEL,
            "capabilities": _get_model_capabilities(model_id),
            "pricing_tier": _get_pricing_tier(model_id),
            "performance_tier": _get_performance_tier(model_id)
        }
        
        return {
            "success": True,
            "model": model_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 정보 조회 실패: {str(e)}"
        )


@router.post("/models/validate")
async def validate_model(model_data: Dict[str, str]):
    """모델이 유효한지 검증"""
    try:
        model_id = model_data.get("model_id")
        
        if not model_id:
            raise HTTPException(
                status_code=400,
                detail="model_id가 필요합니다"
            )
        
        is_valid = model_id in settings.AVAILABLE_MODELS
        
        return {
            "success": True,
            "is_valid": is_valid,
            "model_id": model_id,
            "message": "유효한 모델입니다" if is_valid else "지원하지 않는 모델입니다"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"모델 검증 실패: {str(e)}"
        )


def _get_model_capabilities(model_id: str) -> List[str]:
    """모델별 기능 반환"""
    capabilities_map = {
        "gpt-4.1": ["텍스트 생성", "코드 생성", "복합 추론", "대용량 컨텍스트"],
        "gpt-4.1-mini": ["텍스트 생성", "코드 생성", "빠른 응답"],
        "gpt-4.1-nano": ["텍스트 생성", "실시간 처리", "경량화"],
        "gpt-4o": ["텍스트 생성", "이미지 인식", "멀티모달"],
        "gpt-4o-mini": ["텍스트 생성", "코드 생성", "비용 효율적"],
        "gpt-4-turbo": ["텍스트 생성", "코드 생성", "안정적 성능"],
        "gpt-4": ["텍스트 생성", "코드 생성", "범용적"],
        "gpt-3.5-turbo": ["텍스트 생성", "기본 코드 생성"]
    }
    return capabilities_map.get(model_id, ["텍스트 생성"])


def _get_pricing_tier(model_id: str) -> str:
    """모델별 가격 등급 반환"""
    pricing_map = {
        "gpt-4.1": "premium",
        "gpt-4.1-mini": "standard",
        "gpt-4.1-nano": "economy",
        "gpt-4o": "premium",
        "gpt-4o-mini": "economy",
        "gpt-4-turbo": "premium",
        "gpt-4": "standard",
        "gpt-3.5-turbo": "economy"
    }
    return pricing_map.get(model_id, "standard")


def _get_performance_tier(model_id: str) -> str:
    """모델별 성능 등급 반환"""
    performance_map = {
        "gpt-4.1": "최고",
        "gpt-4.1-mini": "높음",
        "gpt-4.1-nano": "중간",
        "gpt-4o": "최고",
        "gpt-4o-mini": "중간",
        "gpt-4-turbo": "높음",
        "gpt-4": "높음",
        "gpt-3.5-turbo": "기본"
    }
    return performance_map.get(model_id, "기본")
