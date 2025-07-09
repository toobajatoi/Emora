#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Check Python version
echo "📋 Python version:"
python --version

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Build completed successfully!" 