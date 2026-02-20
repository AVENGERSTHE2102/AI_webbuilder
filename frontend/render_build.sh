#!/usr/bin/env bash
# Render build script for frontend

set -o errexit  # Exit on error

echo "📦 Installing Node dependencies..."
npm install

echo "🏗️ Building frontend..."
npm run build

echo "✅ Frontend build complete!"
echo "📁 Build output in: dist/"
