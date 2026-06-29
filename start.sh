#!/bin/bash

echo "=========================================="
echo "Adaptive Learning System - Startup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "Starting the application..."
echo "=========================================="
echo ""
echo "The application will be available at:"
echo "http://localhost:5000"
echo ""
echo "Default Admin Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="
echo ""

# Run the application
python3 app.py