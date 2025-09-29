#!/bin/bash

# ANZx Cricket Agent - Chatbot Deployment Script
# Deploys the cricket chatbot to Cloudflare Pages

set -e

echo "🏏 Deploying ANZx Cricket Agent Chatbot..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the cricket-marketing directory"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm ci

# Build the application
echo "🔨 Building application..."
npm run build

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "📥 Installing Wrangler CLI..."
    npm install -g wrangler@latest
fi

# Deploy to Cloudflare Pages
echo "🚀 Deploying to Cloudflare Pages..."
wrangler pages deploy .next --project-name=anzx-cricket --branch=main

echo "✅ Deployment complete!"
echo "🌐 Your cricket chatbot is now available at: https://anzx.ai/cricket"
