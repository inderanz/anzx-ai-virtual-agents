#!/bin/bash

# ANZX Marketing - Development Environment Setup Script

set -e

echo "🚀 Setting up ANZX Marketing development environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ npm version: $(npm --version)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Copy environment file if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local from example..."
    cp .env.local.example .env.local
    echo "⚠️  Please update .env.local with your configuration"
else
    echo "✅ .env.local already exists"
fi

# Check if gcloud is installed
if command -v gcloud &> /dev/null; then
    echo "✅ gcloud CLI is installed"
    echo "📋 Current gcloud configuration:"
    gcloud config list
    
    # Check if Application Default Credentials are set
    if gcloud auth application-default print-access-token &> /dev/null; then
        echo "✅ Application Default Credentials are configured"
    else
        echo "⚠️  Application Default Credentials not found"
        echo "Run: gcloud auth application-default login"
    fi
else
    echo "⚠️  gcloud CLI is not installed"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p public/images
mkdir -p public/fonts
mkdir -p content/blog
mkdir -p components/layout
mkdir -p components/ui
mkdir -p lib/api
mkdir -p lib/utils

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env.local with your configuration"
echo "2. Run 'npm run dev' to start the development server"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "For Google Cloud integration:"
echo "1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install"
echo "2. Run: gcloud auth application-default login"
echo "3. Set project: gcloud config set project anzx-ai-platform"
echo ""
