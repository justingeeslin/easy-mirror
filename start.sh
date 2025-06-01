#!/bin/bash

# Easy Mirror Startup Script
# This script helps start the Easy Mirror application with proper configuration

echo "🎥 Easy Mirror - Starting up..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.deps_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.deps_installed
fi

# Check for demo mode flag
if [ "$1" = "--demo" ] || [ "$1" = "-d" ]; then
    echo "Starting in DEMO MODE (simulated camera)..."
    export DEMO_MODE=true
else
    echo "Starting with real camera detection..."
fi

# Start the application
echo "Starting Easy Mirror on http://localhost:12000"
echo "Press Ctrl+C to stop"
echo ""

python app.py