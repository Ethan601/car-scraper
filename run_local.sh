#!/bin/bash

# Canadian Used Car Listing Scraper - Local Run Script

echo "🚗 Canadian Used Car Listing Scraper"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Starting application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the application
python3 app.py

