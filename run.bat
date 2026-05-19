@echo off
REM F2C Analytics Panel - Windows Startup Script
REM This script sets up and runs the Streamlit dashboard

setlocal enabledelayedexpansion

echo.
echo =========================================
echo  F2C Analytics Panel - Startup
echo =========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found
    echo Please ensure .env contains SUPABASE_URL and SUPABASE_KEY
    pause
    exit /b 1
)

echo [OK] .env file found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo [SETUP] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo [SETUP] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo.
echo [SETUP] Installing dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Run Streamlit app
echo.
echo =========================================
echo  Launching F2C Analytics Dashboard...
echo  Dashboard URL: http://localhost:8501
echo =========================================
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py --server.port=8501

pause
