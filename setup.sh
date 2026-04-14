#!/bin/bash
# ============================================================
# WebSentinel - Complete Setup Script for Linux/macOS
# ============================================================
# This script will:
# 1. Create a Python virtual environment
# 2. Install all dependencies
# 3. Install Playwright browsers (Chromium for visual testing)
# 4. Verify installation
# ============================================================

echo ""
echo "============================================================"
echo "       WebSentinel - Complete Setup Script"
echo "============================================================"
echo ""

# Check Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10+ first"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

echo "[2/5] Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo "[3/5] Upgrading pip..."
python -m pip install --upgrade pip

echo "[4/5] Installing Python dependencies..."
echo "This may take several minutes..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo "[5/5] Installing Playwright browser (Chromium)..."
echo "This downloads ~170MB for the browser..."
python -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "WARNING: Playwright browser installation may have failed"
    echo "You can retry manually: python -m playwright install chromium"
fi

echo ""
echo "============================================================"
echo "           Setup Complete!"
echo "============================================================"
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Create a .env file with your API key:"
echo "   GOOGLE_API_KEY=your_api_key_here"
echo ""
echo "2. Start Gradio Interface (Visual AI Agent):"
echo "   python launch.py   (then select option 1)"
echo "   OR: python interfaces/web_interface.py"
echo ""
echo "3. Start Streamlit Interface:"
echo "   python launch.py   (then select option 2)"
echo "   OR: streamlit run interfaces/streamlit_interface.py"
echo ""
echo "============================================================"
echo ""
