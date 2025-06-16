"""
Chat service implementing business logic for chat operations.
"""
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, AsyncGenerator

from backend.core.gpt_client import gpt_client
from backend.core.error_handler import error_handler
from backend.core.token_counter import token_counter
from backend.models.chat_models import (
    ChatMessage, ChatRequest, ChatResponse, ConversationRequest, 
    ConversationResponse, TokenInfo, MessageValidation
)
from backend.utils.logger import logger, log_performance


class ChatService:
    """Service class for handling chat operations."""
    
    def __init__(self):
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.statistics = {
            "total_requests": 0,
            "total_tokens": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_response_time": 0.0,
            "error_count": 0
        }
    
    async def validate_messages(
        self, 
        messages: List[ChatMessage],
        max_tokens: Optional[int] = None
    ) -> MessageValidation:
        """
        Validate chat messages for common issues.
        
        Args:
            messages: List of chat messages
            max_tokens: Maximum tokens for response
            
        Returns:
            MessageValidation with validation results
        """
        errors = []
        warnings = []
        
        # Basic validation
        if not messages:
            errors.append("Messages list cannot be empty")
            
        if messages and messages[0].role == 'assistant':
            errors.append("First message cannot be from assistant")
        
        # Check for consecutive messages from same role
        for i in range(1, len(messages)):
            if messages[i].role == messages[i-1].role and messages[i].role != 'system':
                warnings.append(f"Consecutive messages from {messages[i].role} at position {i}")
        
        # Check message content length
        for i, msg in enumerate(messages):
            if len(msg.content.strip()) == 0:
                errors.append(f"Empty message content at position {i}")
            elif len(msg.content) > 10000:  # Arbitrary large message warning
                warnings.append(f"Very long message at position {i} ({len(msg.content)} chars)")
        
        # Token validation
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
        token_info_dict = token_counter.calculate_total_tokens(message_dicts, max_tokens)
        within_limit = token_counter.is_within_limit(message_dicts, max_tokens)
        
        token_info = TokenInfo(
            prompt_tokens=token_info_dict["prompt_tokens"],
            estimated_response_tokens=token_info_dict["estimated_response_tokens"],
            total_tokens=token_info_dict["total_tokens"],
            within_limit=within_limit,
            model_limit=4096  # Default, should be dynamic based on model
        )
        
        if not within_limit:
            errors.append(f"Token limit exceeded: {token_info.total_tokens} > {token_info.model_limit}")
        
        return MessageValidation(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            token_info=token_info
        )
    
    async def chat_completion(self, request: ChatRequest) -> ChatResponse:
        """
        Perform chat completion with validation and error handling.
        
        Args:
            request: Chat completion request
            
        Returns:
            Chat completion response
        """
        start_time = time.time()
        
        try:
            # Validate messages
            message_list = [msg for msg in request.messages]
            validation = await self.validate_messages(message_list, request.max_tokens)
            
            if not validation.valid:
                error_handler.handle_validation_error(
                    f"Message validation failed: {', '.join(validation.errors)}"
                )
            
            # Log warnings
            for warning in validation.warnings:
                logger.warning(f"Message validation warning: {warning}")
            
            # Convert to dict format for API
            message_dicts = [
                {"role": msg.role, "content": msg.content, **({"name": msg.name} if msg.name else {})}
                for msg in message_list
            ]
            
            # Make API call
            with log_performance("gpt_api_call"):
                response = await gpt_client.chat_completion(
                    messages=message_dicts,
                    model=request.model,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    stream=request.stream,
                    use_cache=request.use_cache
                )
            
            # Calculate response time
            response_time = time.time() - start_time
            
            # Update statistics
            self.statistics["total_requests"] += 1
            self.statistics["total_response_time"] += response_time
            
            if response.get("usage"):
                self.statistics["total_tokens"] += response["usage"]["total_tokens"]
            
            # Create response model
            chat_response = ChatResponse(
                id=response["id"],
                object=response["object"],
                created=response["created"],
                model=response["model"],
                choices=response["choices"],
                usage=response.get("usage"),
                cached=False,  # TODO: Detect if response was cached
                response_time=response_time
            )
            
            logger.info(
                "Chat completion successful",
                response_time=f"{response_time:.3f}s",
                tokens_used=response.get("usage", {}).get("total_tokens", 0)
            )
            
            return chat_response
            
        except Exception as e:
            self.statistics["error_count"] += 1
            error_handler.handle_chat_error(e, message_list)
    
    async def stream_chat_completion(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """
        Stream chat completion responses.
        
        Args:
            request: Chat completion request with stream=True
            
        Yields:
            Streaming response chunks
        """
        try:
            # Validate messages
            message_list = [msg for msg in request.messages]
            validation = await self.validate_messages(message_list, request.max_tokens)
            
            if not validation.valid:
                error_handler.handle_validation_error(
                    f"Message validation failed: {', '.join(validation.errors)}"
                )
            
            # Convert to dict format
            message_dicts = [
                {"role": msg.role, "content": msg.content, **({"name": msg.name} if msg.name else {})}
                for msg in message_list
            ]
            
            # Get streaming response
            response_stream = await gpt_client.chat_completion(
                messages=message_dicts,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                use_cache=False  # Disable caching for streaming
            )
            
            # Stream the response
            async for chunk in response_stream:
                if hasattr(chunk, 'choices') and chunk.choices:
                    choice = chunk.choices[0]
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                        if choice.delta.content:
                            yield choice.delta.content
            
            # Update statistics
            self.statistics["total_requests"] += 1
            
        except Exception as e:
            self.statistics["error_count"] += 1
            error_handler.handle_chat_error(e, message_list)
    
    async def conversation_chat(self, request: ConversationRequest) -> ConversationResponse:
        """
        Handle conversation with context management.
        
        Args:
            request: Conversation request
            
        Returns:
            Conversation response with context
        """
        try:
            # Generate or use existing conversation ID
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # Get existing conversation history
            conversation_history = self.conversations.get(conversation_id, [])
            
            # Add system prompt if provided
            messages = []
            if request.system_prompt:
                messages.append(ChatMessage(role="system", content=request.system_prompt))
            
            # Add relevant context messages
            context_messages = conversation_history[-request.context_length:] if conversation_history else []
            messages.extend(context_messages)
            
            # Add current user message
            user_message = ChatMessage(role="user", content=request.message)
            messages.append(user_message)
            
            # Create chat request
            chat_request = ChatRequest(
                messages=messages,
                use_cache=True
            )
            
            # Get response
            response = await self.chat_completion(chat_request)
            
            # Extract assistant message
            assistant_content = response.choices[0]["message"]["content"]
            assistant_message = ChatMessage(role="assistant", content=assistant_content)
            
            # Update conversation history
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            self.conversations[conversation_id].extend([user_message, assistant_message])
            
            # Trim conversation history if too long (keep last 100 messages)
            if len(self.conversations[conversation_id]) > 100:
                self.conversations[conversation_id] = self.conversations[conversation_id][-100:]
            
            return ConversationResponse(
                conversation_id=conversation_id,
                message=assistant_content,
                usage=response.usage or {},
                context_messages=len(context_messages),
                cached=response.cached
            )
            
        except Exception as e:
            error_handler.handle_chat_error(e, messages if 'messages' in locals() else [])
    
    async def get_conversation_history(self, conversation_id: str) -> List[ChatMessage]:
        """Get conversation history by ID."""
        return self.conversations.get(conversation_id, [])
    
    async def clear_conversation(self, conversation_id: str) -> bool:
        """Clear conversation history."""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation: {conversation_id}")
            return True
        return False
    
    async def get_statistics(self) -> Dict:
        """Get chat service statistics."""
        avg_response_time = (
            self.statistics["total_response_time"] / self.statistics["total_requests"]
            if self.statistics["total_requests"] > 0 else 0
        )
        
        error_rate = (
            (self.statistics["error_count"] / self.statistics["total_requests"]) * 100
            if self.statistics["total_requests"] > 0 else 0
        )
        
        # Get API usage stats
        api_stats = await gpt_client.get_usage_stats()
        
        return {
            "chat_service": {
                "total_requests": self.statistics["total_requests"],
                "total_tokens": self.statistics["total_tokens"],
                "average_response_time": avg_response_time,
                "error_rate": error_rate,
                "active_conversations": len(self.conversations)
            },
            "api_stats": api_stats
        }
    
    async def health_check(self) -> Dict:
        """Perform health check on chat service."""
        try:
            # Test basic chat completion
            test_request = ChatRequest(
                messages=[ChatMessage(role="user", content="Hello")],
                max_tokens=10,
                use_cache=False
            )
            
            start_time = time.time()
            response = await self.chat_completion(test_request)
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "api_accessible": True,
                "cache_accessible": True,  # TODO: Add actual cache check
                "test_response": response.choices[0]["message"]["content"] if response.choices else ""
            }
            
        except Exception as e:
            logger.error(f"Chat service health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_accessible": False
            }


# Global chat service instance
chat_service = ChatService()
