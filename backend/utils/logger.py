"""
Structured logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from config.settings import settings


def setup_logging():
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )
    
    # Create file handler for persistent logging
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter for file logs
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    
    # Add file handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


# Setup logging when module is imported
setup_logging()

# Create logger instance
logger = structlog.get_logger(__name__)


class LoggerMixin:
    """Mixin class to add logging capabilities to other classes."""
    
    @property
    def logger(self):
        """Get logger instance for the class."""
        return structlog.get_logger(self.__class__.__name__)


def log_api_call(func):
    """Decorator to log API calls with timing information."""
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting API call: {func.__name__}")
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(
                f"API call completed: {func.__name__}",
                duration=f"{duration:.3f}s",
                success=True
            )
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"API call failed: {func.__name__}",
                duration=f"{duration:.3f}s",
                error=str(e),
                success=False
            )
            raise
    
    return wrapper


def log_performance(operation_name: str):
    """Context manager for logging performance metrics."""
    import time
    from contextlib import contextmanager
    
    @contextmanager
    def performance_logger():
        start_time = time.time()
        logger.debug(f"Starting operation: {operation_name}")
        
        try:
            yield
            duration = time.time() - start_time
            logger.info(
                f"Operation completed: {operation_name}",
                duration=f"{duration:.3f}s",
                success=True
            )
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Operation failed: {operation_name}",
                duration=f"{duration:.3f}s",
                error=str(e),
                success=False
            )
            raise
    
    return performance_logger()
