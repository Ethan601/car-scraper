@echo off
REM Canadian Used Car Listing Scraper - Local Run Script for Windows

echo.
echo 🚗 Canadian Used Car Listing Scraper
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found: 
python --version
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Starting application...
echo 📱 Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run the application
python app.py

pause

