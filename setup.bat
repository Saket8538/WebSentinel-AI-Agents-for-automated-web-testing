@echo off
REM WebSentinel Setup Script for Windows
REM =====================================
REM Run this script on a new laptop to set up everything

echo ============================================
echo WebSentinel - Setup Script
echo ============================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call .\.venv\Scripts\activate

echo [3/5] Upgrading pip...
python -m pip install --upgrade pip

echo [4/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [5/5] Installing Playwright browsers (required for visual testing)...
python -m playwright install chromium
if errorlevel 1 (
    echo WARNING: Failed to install Playwright browsers
    echo You can try manually: python -m playwright install chromium
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo NEXT STEPS:
echo 1. Create a .env file with your GOOGLE_API_KEY
echo 2. Run: python launch.py
echo.
echo Or start interfaces directly:
echo   Gradio:    python interfaces/web_interface.py
echo   Streamlit: streamlit run interfaces/streamlit_interface.py
echo.
pause
