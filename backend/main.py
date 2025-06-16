"""
Main FastAPI application with CORS, middleware, and route configuration.
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config.settings import settings
from backend.api import chat, system
from backend.core.error_handler import APIError, create_error_response
from backend.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Local AI Agent application")
    logger.info(f"Configuration: Model={settings.openai_model}, Cache={settings.cache_type}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Local AI Agent application")


# Create FastAPI application
app = FastAPI(
    title="Local AI Agent",
    description="Local AI Agent with GPT API integration, caching, and extensible architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests."""
    start_time = logger.time.time()
    
    # Log request
    logger.info(
        f"HTTP Request: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = logger.time.time() - start_time
    logger.info(
        f"HTTP Response: {response.status_code}",
        status_code=response.status_code,
        duration=f"{duration:.3f}s"
    )
    
    return response


@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors."""
    error_response = create_error_response(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    error_response = create_error_response(
        APIError("Internal server error", "INTERNAL_ERROR")
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    )


# Include API routers
app.include_router(chat.router)
app.include_router(system.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Local AI Agent API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "chat": "/api/chat",
            "system": "/api/system"
        }
    }


@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": logger.time.time(),
        "version": "1.0.0"
    }


# Mount static files for frontend (if frontend directory exists)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/app")
    async def serve_frontend():
        """Serve the frontend application."""
        return JSONResponse({"message": "Frontend will be served from /static"})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
        log_level=settings.log_level.lower()
    )
