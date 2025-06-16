#!/bin/bash

# Local AI Agent Backend Startup Script
# 개선된 버전으로 더 나은 에러 핸들링과 로깅 제공

set -e  # Exit on any error

echo "🚀 Starting Local AI Agent Backend..."
echo "======================================="

# Change to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

# Verify OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY not found or invalid in .env file"
    echo "   Please set your OpenAI API key in the .env file"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/logs
mkdir -p data/cache
mkdir -p data/backups
mkdir -p data/workspace
mkdir -p data/temp

# Check Python dependencies
echo "🔍 Checking dependencies..."
python -c "import fastapi, uvicorn, openai, aiohttp, diskcache, aiofiles, watchdog" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

# Set development mode environment variable
export DEVELOPMENT_MODE=true

echo "✅ Environment ready!"
echo ""
echo "🌐 Starting FastAPI server..."
echo "   API will be available at: http://localhost:8000"
echo "   API documentation: http://localhost:8000/docs"
echo "   ReDoc documentation: http://localhost:8000/redoc"
echo ""
echo "📊 Monitoring endpoints:"
echo "   Health check: http://localhost:8000/health"
echo "   Agent health: http://localhost:8000/api/agent/health"
echo "   Available tools: http://localhost:8000/api/agent/tools"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================="

# Start the server with better error handling
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
