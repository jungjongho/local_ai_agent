"""
Pydantic models for chat-related operations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class ChatMessage(BaseModel):
    """Individual chat message model."""
    role: str = Field(..., description="Message role (system, user, assistant)")
    content: str = Field(..., description="Message content")
    name: Optional[str] = Field(None, description="Optional name for the message author")
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ['system', 'user', 'assistant', 'function']
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of {allowed_roles}")
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class ChatRequest(BaseModel):
    """Chat completion request model."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    model: Optional[str] = Field(None, description="OpenAI model to use")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(None, ge=1, le=8000, description="Maximum tokens in response")
    stream: bool = Field(False, description="Whether to stream the response")
    use_cache: bool = Field(True, description="Whether to use response caching")
    
    @validator('messages')
    def validate_messages(cls, v):
        if not v:
            raise ValueError("Messages list cannot be empty")
        
        # Ensure first message is not from assistant
        if v[0].role == 'assistant':
            raise ValueError("First message cannot be from assistant")
        
        return v


class ChatResponse(BaseModel):
    """Chat completion response model."""
    id: str = Field(..., description="Unique response ID")
    object: str = Field(..., description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used")
    choices: List[Dict[str, Any]] = Field(..., description="Response choices")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")
    cached: bool = Field(False, description="Whether response was served from cache")
    response_time: Optional[float] = Field(None, description="Response time in seconds")


class StreamChunk(BaseModel):
    """Streaming response chunk model."""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]


class ConversationRequest(BaseModel):
    """Request for managing conversation context."""
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    message: str = Field(..., description="User message")
    context_length: Optional[int] = Field(10, ge=1, le=50, description="Number of previous messages to include")
    system_prompt: Optional[str] = Field(None, description="Optional system prompt override")


class ConversationResponse(BaseModel):
    """Response for conversation with context."""
    conversation_id: str = Field(..., description="Conversation ID")
    message: str = Field(..., description="Assistant response")
    usage: Dict[str, int] = Field(..., description="Token usage")
    context_messages: int = Field(..., description="Number of context messages used")
    cached: bool = Field(False, description="Whether response was cached")


class ChatStatistics(BaseModel):
    """Chat service statistics model."""
    total_requests: int = Field(..., description="Total number of requests")
    total_tokens: int = Field(..., description="Total tokens consumed")
    cache_hits: int = Field(..., description="Number of cache hits")
    cache_misses: int = Field(..., description="Number of cache misses")
    average_response_time: float = Field(..., description="Average response time in seconds")
    error_rate: float = Field(..., description="Error rate percentage")


class TokenInfo(BaseModel):
    """Token counting information."""
    prompt_tokens: int = Field(..., description="Tokens in the prompt")
    estimated_response_tokens: int = Field(..., description="Estimated tokens for response")
    total_tokens: int = Field(..., description="Total estimated tokens")
    within_limit: bool = Field(..., description="Whether request is within token limits")
    token_limit: int = Field(..., description="Model's token limit")


class MessageValidation(BaseModel):
    """Message validation result."""
    valid: bool = Field(..., description="Whether messages are valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    token_info: Optional[TokenInfo] = Field(None, description="Token usage information")


# Example usage and validation models
class ExampleChatFlow(BaseModel):
    """Example of a complete chat flow for documentation."""
    step: str
    description: str
    request_example: Optional[Dict[str, Any]] = None
    response_example: Optional[Dict[str, Any]] = None


# Conversation history models (for future Phase 3 implementation)
class ConversationHistory(BaseModel):
    """Conversation history model for persistence."""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ConversationSummary(BaseModel):
    """Conversation summary for context management."""
    conversation_id: str
    summary: str
    message_count: int
    total_tokens: int
    last_activity: datetime
