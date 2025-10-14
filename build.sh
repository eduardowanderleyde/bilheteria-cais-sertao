#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🔧 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed successfully!"

echo "📊 Creating database tables..."
python -c "from app.db import engine, Base; Base.metadata.create_all(bind=engine)"

echo "👤 Creating admin user and default users..."
python seed_admin.py

echo "✅ Build completed successfully!"