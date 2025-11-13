#!/bin/bash
# Quick start script for Selenium Python tests

set -e

echo "🚀 Bagisto Selenium Python - Quick Start"
echo "========================================"

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
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Please create .env with your Bagisto credentials:"
    echo "   BAGISTO_EMAIL=your-email@example.com"
    echo "   BAGISTO_PASSWORD=your-password"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Run tests with:"
echo "  pytest tests/test_bagisto_s1_single_checkout.py -v -s"
echo ""
echo "Or run all tests:"
echo "  pytest tests/ -v"
echo ""
