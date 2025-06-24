"""
Configuration settings for the Local AI Agent.
Uses pydantic-settings for type-safe configuration management.
"""
import os
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and type safety."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")
    openai_max_tokens: int = Field(default=4000, ge=1, le=8000)
    openai_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    
    # Cache Configuration
    cache_type: Literal["disk", "redis"] = Field(default="disk")
    cache_ttl: int = Field(default=3600, ge=0, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, ge=1)
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8025, ge=1, le=65535)
    api_debug: bool = Field(default=False)
    
    # Rate Limiting
    max_requests_per_minute: int = Field(default=60, ge=1)
    max_tokens_per_hour: int = Field(default=100000, ge=1000)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="data/logs/app.log")
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production", description="Secret key for security")
    
    # Redis Configuration (for future use)
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379, ge=1, le=65535)
    redis_db: int = Field(default=0, ge=0)
    
    # File Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    cache_dir: Path = Field(default_factory=lambda: Path("data/cache"))
    logs_dir: Path = Field(default_factory=lambda: Path("data/logs"))
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __post_init__(self):
        """Create necessary directories after initialization."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def cache_path(self) -> Path:
        """Get the cache directory path."""
        return self.project_root / self.cache_dir
    
    @property
    def log_path(self) -> Path:
        """Get the log file path."""
        return self.project_root / self.log_file


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.cache_path.mkdir(parents=True, exist_ok=True)
settings.log_path.parent.mkdir(parents=True, exist_ok=True)
