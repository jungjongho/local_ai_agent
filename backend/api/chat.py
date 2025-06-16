"""
Chat API endpoints for handling chat requests.
"""
from typing import Dict, List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from backend.models.chat_models import (
    ChatRequest, ChatResponse, ConversationRequest, ConversationResponse,
    ChatMessage, MessageValidation
)
from backend.services.chat_service import chat_service
from backend.utils.logger import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/completion", response_model=ChatResponse)
async def chat_completion(request: ChatRequest) -> ChatResponse:
    """
    Create a chat completion.
    
    This endpoint handles single chat completion requests with optional caching
    and supports various OpenAI models and parameters.
    
    Args:
        request: Chat completion request with messages and parameters
        
    Returns:
        Chat completion response with generated content
        
    Raises:
        HTTPException: For validation errors, API errors, or rate limits
    """
    logger.info(f"Chat completion request with {len(request.messages)} messages")
    
    try:
        response = await chat_service.chat_completion(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise


@router.post("/stream")
async def stream_chat_completion(request: ChatRequest):
    """
    Create a streaming chat completion.
    
    This endpoint streams the chat completion response in real-time,
    useful for long responses or interactive applications.
    
    Args:
        request: Chat completion request (stream parameter ignored)
        
    Returns:
        StreamingResponse with chat completion chunks
    """
    logger.info(f"Streaming chat completion request with {len(request.messages)} messages")
    
    async def generate_stream():
        try:
            # Force streaming mode
            request.stream = True
            
            async for chunk in chat_service.stream_chat_completion(request):
                # Send each chunk as server-sent events
                yield f"data: {chunk}\n\n"
                
            # Send end marker
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming chat: {e}")
            yield f"data: ERROR: {str(e)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/conversation", response_model=ConversationResponse)
async def conversation_chat(request: ConversationRequest) -> ConversationResponse:
    """
    Chat with conversation context management.
    
    This endpoint maintains conversation history and context,
    making it easier to have multi-turn conversations.
    
    Args:
        request: Conversation request with message and context settings
        
    Returns:
        Conversation response with context information
    """
    logger.info(f"Conversation chat request: {request.conversation_id}")
    
    try:
        response = await chat_service.conversation_chat(request)
        return response
        
    except Exception as e:
        logger.error(f"Error in conversation chat: {e}")
        raise


@router.post("/validate", response_model=MessageValidation)
async def validate_messages(messages: List[ChatMessage]) -> MessageValidation:
    """
    Validate chat messages for common issues.
    
    This endpoint checks messages for validation errors, warnings,
    and token usage before making API calls.
    
    Args:
        messages: List of chat messages to validate
        
    Returns:
        Message validation results with errors and warnings
    """
    logger.debug(f"Validating {len(messages)} messages")
    
    try:
        validation = await chat_service.validate_messages(messages)
        return validation
        
    except Exception as e:
        logger.error(f"Error validating messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )


@router.get("/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str) -> List[ChatMessage]:
    """
    Get conversation history by ID.
    
    Args:
        conversation_id: Conversation identifier
        
    Returns:
        List of messages in the conversation
    """
    logger.debug(f"Getting conversation history: {conversation_id}")
    
    try:
        history = await chat_service.get_conversation_history(conversation_id)
        return history
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str) -> Dict[str, bool]:
    """
    Clear conversation history.
    
    Args:
        conversation_id: Conversation identifier
        
    Returns:
        Success status
    """
    logger.info(f"Clearing conversation: {conversation_id}")
    
    try:
        success = await chat_service.clear_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        return {"success": success}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing conversation: {str(e)}"
        )


@router.get("/statistics")
async def get_chat_statistics() -> Dict:
    """
    Get chat service statistics.
    
    Returns comprehensive statistics about chat service usage,
    including API usage, cache performance, and error rates.
    
    Returns:
        Dictionary with various statistics
    """
    logger.debug("Getting chat statistics")
    
    try:
        stats = await chat_service.get_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict:
    """
    Perform health check on chat service.
    
    This endpoint tests the chat service functionality including
    API connectivity, cache accessibility, and basic operations.
    
    Returns:
        Health status information
    """
    logger.debug("Performing chat service health check")
    
    try:
        health_status = await chat_service.health_check()
        
        # Return appropriate HTTP status based on health
        if health_status["status"] != "healthy":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=health_status
            )
        
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "unhealthy", "error": str(e)}
        )


# Example endpoint for testing (can be removed in production)
@router.post("/test")
async def test_chat() -> Dict:
    """
    Simple test endpoint for quick verification.
    
    Returns:
        Test response
    """
    try:
        test_request = ChatRequest(
            messages=[ChatMessage(role="user", content="Say hello!")],
            max_tokens=20
        )
        
        response = await chat_service.chat_completion(test_request)
        
        return {
            "status": "success",
            "test_response": response.choices[0]["message"]["content"] if response.choices else "",
            "tokens_used": response.usage["total_tokens"] if response.usage else 0
        }
        
    except Exception as e:
        logger.error(f"Test endpoint failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }
