#!/usr/bin/env bash
# Render build script for backend

set -o errexit  # Exit on error

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend build complete!"
