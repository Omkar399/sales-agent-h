#!/bin/bash

# Sales Agent Dashboard - Stop All Services Script

echo "🛑 Stopping Sales Agent Dashboard Services..."
echo "============================================="

# Function to stop process by pattern
stop_process() {
    local pattern=$1
    local name=$2
    
    pids=$(pgrep -f "$pattern")
    if [ ! -z "$pids" ]; then
        echo "🔴 Stopping $name (PIDs: $pids)..."
        pkill -f "$pattern"
        sleep 2
        
        # Check if processes are still running
        remaining_pids=$(pgrep -f "$pattern")
        if [ ! -z "$remaining_pids" ]; then
            echo "⚠️  Force killing $name (PIDs: $remaining_pids)..."
            pkill -9 -f "$pattern"
        fi
        echo "✅ $name stopped"
    else
        echo "ℹ️  $name is not running"
    fi
}

# Stop backend (FastAPI/Uvicorn)
stop_process "uvicorn app.main:app" "Backend Server"

# Stop frontend (Vite)
stop_process "vite" "Frontend Server"

# Stop any remaining Node.js processes related to our frontend
stop_process "node.*vite" "Frontend Node Processes"

echo ""
echo "🎯 Checking for remaining processes..."

# Check if any processes are still running
backend_check=$(pgrep -f "uvicorn app.main:app")
frontend_check=$(pgrep -f "vite")

if [ -z "$backend_check" ] && [ -z "$frontend_check" ]; then
    echo "✅ All Sales Agent Dashboard services stopped successfully"
else
    echo "⚠️  Some processes might still be running:"
    if [ ! -z "$backend_check" ]; then
        echo "   • Backend: $backend_check"
    fi
    if [ ! -z "$frontend_check" ]; then
        echo "   • Frontend: $frontend_check"
    fi
fi

# Check ports
echo ""
echo "🔍 Port status:"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   • Port 8000: Still in use"
else
    echo "   • Port 8000: Free ✅"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "   • Port 3000: Still in use"
else
    echo "   • Port 3000: Free ✅"
fi

echo ""
echo "👋 Sales Agent Dashboard services stopped"
echo "💡 To start again, run: ./start-all.sh"
