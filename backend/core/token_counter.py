"""
Token counting utilities using tiktoken.
Provides accurate token counting for various OpenAI models.
"""
import tiktoken
from typing import Dict, List, Optional
from functools import lru_cache

from config.settings import settings


class TokenCounter:
    """Token counting and management for OpenAI API calls."""
    
    def __init__(self, model: str = None):
        self.model = model or settings.openai_model
        self._encoding = self._get_encoding()
    
    @lru_cache(maxsize=128)
    def _get_encoding(self) -> tiktoken.Encoding:
        """Get tiktoken encoding for the model with caching."""
        try:
            return tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Fallback to cl100k_base for unknown models
            return tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in a single text string."""
        if not text:
            return 0
        return len(self._encoding.encode(text))
    
    def count_message_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Count tokens in a list of messages for chat completion.
        
        Based on OpenAI's token counting guidelines:
        https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        """
        if not messages:
            return 0
        
        # Model-specific token counting
        if self.model in ["gpt-3.5-turbo", "gpt-3.5-turbo-0613"]:
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name = -1  # if there's a name, the role is omitted
        elif self.model in ["gpt-4", "gpt-4-0613"]:
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            # Default values for unknown models
            tokens_per_message = 3
            tokens_per_name = 1
        
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                if isinstance(value, str):
                    num_tokens += self.count_tokens(value)
                    if key == "name":
                        num_tokens += tokens_per_name
        
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens
    
    def estimate_response_tokens(self, max_tokens: Optional[int] = None) -> int:
        """Estimate tokens that will be used for the response."""
        return max_tokens or settings.openai_max_tokens
    
    def calculate_total_tokens(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None
    ) -> Dict[str, int]:
        """Calculate total tokens including prompt and estimated response."""
        prompt_tokens = self.count_message_tokens(messages)
        response_tokens = self.estimate_response_tokens(max_tokens)
        total_tokens = prompt_tokens + response_tokens
        
        return {
            "prompt_tokens": prompt_tokens,
            "estimated_response_tokens": response_tokens,
            "total_tokens": total_tokens
        }
    
    def is_within_limit(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        model_limit: Optional[int] = None
    ) -> bool:
        """Check if the request is within token limits."""
        if model_limit is None:
            # Common model limits
            model_limits = {
                "gpt-3.5-turbo": 4096,
                "gpt-3.5-turbo-16k": 16384,
                "gpt-4": 8192,
                "gpt-4-32k": 32768,
            }
            model_limit = model_limits.get(self.model, 4096)
        
        token_info = self.calculate_total_tokens(messages, max_tokens)
        return token_info["total_tokens"] <= model_limit
    
    def truncate_messages(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: Optional[int] = None,
        preserve_system: bool = True
    ) -> List[Dict[str, str]]:
        """
        Truncate messages to fit within token limits.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens for response
            preserve_system: Whether to preserve system messages
        
        Returns:
            Truncated list of messages
        """
        if self.is_within_limit(messages, max_tokens):
            return messages
        
        # Separate system messages if preserving them
        system_messages = []
        other_messages = []
        
        for msg in messages:
            if preserve_system and msg.get("role") == "system":
                system_messages.append(msg)
            else:
                other_messages.append(msg)
        
        # Calculate available tokens for non-system messages
        system_tokens = self.count_message_tokens(system_messages)
        response_tokens = self.estimate_response_tokens(max_tokens)
        available_tokens = (
            settings.openai_max_tokens - system_tokens - response_tokens - 100  # Safety margin
        )
        
        # Keep messages from the end until we exceed available tokens
        truncated_messages = []
        current_tokens = 0
        
        for msg in reversed(other_messages):
            msg_tokens = self.count_message_tokens([msg])
            if current_tokens + msg_tokens > available_tokens:
                break
            truncated_messages.insert(0, msg)
            current_tokens += msg_tokens
        
        return system_messages + truncated_messages


# Global token counter instance
token_counter = TokenCounter()
