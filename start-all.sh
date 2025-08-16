#!/bin/bash

# Sales Agent Dashboard - Complete Startup Script

echo "🚀 Starting Sales Agent Dashboard (Full Stack)"
echo "=============================================="

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use (Backend)"
    echo "   Please stop the process using port 8000 or change the backend port"
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use (Frontend)"
    echo "   Please stop the process using port 3000 or change the frontend port"
fi

echo ""
echo "🎯 This will start both backend and frontend servers:"
echo "   • Backend (FastAPI):  http://localhost:8000"
echo "   • Frontend (React):   http://localhost:3000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""

# Check for required tools
echo "🔍 Checking prerequisites..."

if ! command -v uv &> /dev/null; then
    echo "❌ UV package manager not found. Install with:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

echo "✅ All prerequisites found"

# Setup backend environment
echo ""
echo "🔧 Setting up backend..."
cd backend

if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit backend/.env and add your GEMINI_API_KEY"
    echo "   Without it, AI features won't work!"
fi

# Install backend dependencies
echo "📦 Installing backend dependencies..."
uv sync

# Create sample data
echo "📊 Setting up sample data..."
uv run python sample_data.py

cd ..

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

cd ..

# Start both services
echo ""
echo "🚀 Starting services..."
echo "⚠️  Both servers will run in the background"
echo "🔧 Use Ctrl+C to stop this script (servers will continue running)"
echo "💡 To stop servers manually:"
echo "   • Backend: pkill -f 'uvicorn app.main:app'"
echo "   • Frontend: pkill -f 'vite'"
echo ""

# Start backend in background
echo "🎯 Starting backend server..."
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both to be ready
echo "⏳ Waiting for servers to start..."
sleep 5

echo ""
echo "🎉 Sales Agent Dashboard is ready!"
echo "=================================="
echo ""
echo "📍 URLs:"
echo "   • Frontend:        http://localhost:3000"
echo "   • Backend API:     http://localhost:8000"
echo "   • API Docs:        http://localhost:8000/docs"
echo "   • Interactive API: http://localhost:8000/redoc"
echo ""
echo "🤖 AI Features:"
echo "   • Gemini Chat Assistant"
echo "   • Google Calendar Integration"
echo "   • HubSpot CRM Integration"
echo "   • Email Automation"
echo ""
echo "📊 Sample Data:"
echo "   • 10 customer cards across all stages"
echo "   • Ready for testing and demo"
echo ""
echo "⚠️  Important:"
echo "   • Add your GEMINI_API_KEY to backend/.env for AI features"
echo "   • Configure other API keys for full functionality"
echo ""
echo "🔧 Process IDs:"
echo "   • Backend PID: $BACKEND_PID"
echo "   • Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop monitoring (servers will continue running)"

# Wait for user to stop
trap 'echo ""; echo "👋 Stopping monitoring. Servers are still running."; echo "💡 To stop servers: ./stop-all.sh"; exit 0' INT

# Keep script running to monitor
while true; do
    sleep 30
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend server stopped unexpectedly"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend server stopped unexpectedly" 
        break
    fi
done
