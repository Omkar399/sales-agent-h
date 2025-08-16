#!/bin/bash

# Sales Agent Dashboard - Frontend Startup Script

echo "🎨 Starting Sales Agent Dashboard Frontend..."

# Navigate to frontend directory
cd frontend

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🎯 Starting React development server..."
echo "📍 Frontend will be available at: http://localhost:3000"
echo "🔄 Hot reload enabled - changes will be reflected automatically"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

npm run dev
