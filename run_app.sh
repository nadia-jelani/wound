#!/bin/bash

echo "🚀 Setting up Wound Whisperer..."

# Create virtual environment if it doesn't exist
if [ ! -d "wound_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv wound_env
fi

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source wound_env/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run the application
echo "🎯 Starting Wound Whisperer on http://localhost:5000"
echo "⚠️  Remember: This is for educational purposes only!"
echo ""
python analyze_wound.py