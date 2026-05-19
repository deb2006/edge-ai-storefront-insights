#!/bin/bash

# F2C Analytics Panel - Unix/macOS Startup Script
# This script sets up and runs the Streamlit dashboard

set -e  # Exit on error

echo ""
echo "========================================="
echo " F2C Analytics Panel - Startup"
echo "========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please ensure .env contains SUPABASE_URL and SUPABASE_KEY"
    exit 1
fi

echo "✓ .env file found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "[SETUP] Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "[SETUP] Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "[SETUP] Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Run Streamlit app
echo ""
echo "========================================="
echo " Launching F2C Analytics Dashboard..."
echo " Dashboard URL: http://localhost:8501"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

streamlit run app.py --server.port=8501
