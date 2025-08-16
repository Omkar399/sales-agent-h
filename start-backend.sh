#!/bin/bash

# Sales Agent Dashboard - Backend Startup Script

echo "🚀 Starting Sales Agent Dashboard Backend..."

# Navigate to backend directory
cd backend

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV package manager is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        echo "✅ Created .env file from template"
        echo "📝 Please edit .env file and add your GEMINI_API_KEY"
        echo "   Required: GEMINI_API_KEY=your_api_key_here"
    else
        echo "❌ env.example file not found"
        exit 1
    fi
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Check if GEMINI_API_KEY is set
if grep -q "GEMINI_API_KEY=your_gemini_api_key_here" .env || grep -q "GEMINI_API_KEY=$" .env; then
    echo "⚠️  GEMINI_API_KEY not configured in .env file"
    echo "   Please add your Gemini API key to .env file"
    echo "   The AI features will not work without it"
fi

# Start the FastAPI server
echo "🎯 Starting FastAPI server..."
echo "📍 Backend will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
