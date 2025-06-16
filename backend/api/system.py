"""
System management API endpoints.
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status

from core.gpt_client import gpt_client
from core.cache_manager import cache_manager
from config.settings import settings
from utils.logger import logger

router = APIRouter(prefix="/api/system", tags=["system"])


@router.get("/health")
async def system_health() -> Dict[str, Any]:
    """
    Get overall system health status.
    
    Returns comprehensive health information for all system components
    including API connectivity, cache status, and configuration.
    
    Returns:
        System health status dictionary
    """
    logger.debug("Performing system health check")
    
    try:
        # Check GPT API health
        api_health = await gpt_client.health_check()
        
        # Check cache health
        cache_stats = await cache_manager.get_stats()
        cache_healthy = "error" not in cache_stats
        
        # Overall system status
        system_healthy = (
            api_health.get("status") == "healthy" and 
            cache_healthy
        )
        
        health_info = {
            "status": "healthy" if system_healthy else "unhealthy",
            "timestamp": time.time(),
            "components": {
                "api": {
                    "status": api_health.get("status", "unknown"),
                    "accessible": api_health.get("api_accessible", False)
                },
                "cache": {
                    "status": "healthy" if cache_healthy else "unhealthy",
                    "type": cache_stats.get("type", "unknown"),
                    "accessible": cache_healthy
                },
                "configuration": {
                    "status": "healthy",
                    "model": settings.openai_model,
                    "cache_type": settings.cache_type
                }
            },
            "details": {
                "api_details": api_health,
                "cache_details": cache_stats
            }
        }
        
        if not system_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_info
            )
        
        return health_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@router.get("/status")
async def system_status() -> Dict[str, Any]:
    """
    Get system status and statistics.
    
    Returns:
        System status information
    """
    logger.debug("Getting system status")
    
    try:
        # Get API usage stats
        api_stats = await gpt_client.get_usage_stats()
        
        # Get cache stats
        cache_stats = await cache_manager.get_stats()
        
        return {
            "status": "running",
            "uptime": "unknown",  # TODO: Implement uptime tracking
            "configuration": {
                "model": settings.openai_model,
                "cache_type": settings.cache_type,
                "max_tokens": settings.openai_max_tokens,
                "temperature": settings.openai_temperature
            },
            "usage": api_stats,
            "cache": cache_stats
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system status: {str(e)}"
        )


@router.get("/config")
async def get_configuration() -> Dict[str, Any]:
    """
    Get system configuration (non-sensitive values only).
    
    Returns:
        System configuration dictionary
    """
    logger.debug("Getting system configuration")
    
    try:
        config = {
            "openai": {
                "model": settings.openai_model,
                "max_tokens": settings.openai_max_tokens,
                "temperature": settings.openai_temperature
            },
            "cache": {
                "type": settings.cache_type,
                "ttl": settings.cache_ttl,
                "max_size": settings.cache_max_size
            },
            "api": {
                "host": settings.api_host,
                "port": settings.api_port,
                "debug": settings.api_debug
            },
            "rate_limiting": {
                "max_requests_per_minute": settings.max_requests_per_minute,
                "max_tokens_per_hour": settings.max_tokens_per_hour
            },
            "logging": {
                "level": settings.log_level,
                "file": settings.log_file
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving configuration: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, bool]:
    """
    Clear all cache entries.
    
    Returns:
        Success status
    """
    logger.info("Clearing system cache")
    
    try:
        success = await cache_manager.clear()
        
        if success:
            logger.info("Cache cleared successfully")
        else:
            logger.warning("Cache clear operation returned false")
        
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_statistics() -> Dict[str, Any]:
    """
    Get detailed cache statistics.
    
    Returns:
        Cache statistics dictionary
    """
    logger.debug("Getting cache statistics")
    
    try:
        stats = await cache_manager.get_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cache statistics: {str(e)}"
        )


@router.get("/metrics")
async def get_system_metrics() -> Dict[str, Any]:
    """
    Get comprehensive system metrics.
    
    Returns:
        System metrics including performance and usage data
    """
    logger.debug("Getting system metrics")
    
    try:
        # Get API usage stats
        api_stats = await gpt_client.get_usage_stats()
        
        # Get cache stats
        cache_stats = await cache_manager.get_stats()
        
        # TODO: Add more metrics like memory usage, response times, etc.
        metrics = {
            "api_metrics": api_stats,
            "cache_metrics": cache_stats,
            "system_metrics": {
                "memory_usage": "not_implemented",
                "cpu_usage": "not_implemented",
                "disk_usage": "not_implemented"
            }
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving system metrics: {str(e)}"
        )


# Future endpoints for Phase 2, 3, 4 functionality
@router.get("/agents/status")
async def get_agent_status() -> Dict[str, Any]:
    """
    Get agent system status (Phase 2 feature).
    
    Returns:
        Agent status information
    """
    return {
        "status": "not_implemented",
        "message": "Agent functionality will be implemented in Phase 2",
        "available_agents": [],
        "active_agents": 0
    }


@router.get("/integrations/status")
async def get_integration_status() -> Dict[str, Any]:
    """
    Get local system integration status (Phase 3 feature).
    
    Returns:
        Integration status information
    """
    return {
        "status": "not_implemented",
        "message": "System integration functionality will be implemented in Phase 3",
        "available_integrations": [],
        "active_integrations": 0
    }


@router.get("/optimization/status")
async def get_optimization_status() -> Dict[str, Any]:
    """
    Get optimization features status (Phase 4 feature).
    
    Returns:
        Optimization status information
    """
    return {
        "status": "not_implemented",
        "message": "Advanced optimization features will be implemented in Phase 4",
        "features": {
            "smart_caching": False,
            "request_batching": False,
            "offline_mode": False
        }
    }
