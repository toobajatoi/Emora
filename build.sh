#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Check Python version
echo "📋 Python version:"
python --version

# Upgrade pip and install build tools
echo "🔧 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Build completed successfully!" 