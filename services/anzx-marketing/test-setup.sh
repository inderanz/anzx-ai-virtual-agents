#!/bin/bash

# ANZX Marketing - Local Test Setup Script

set -e

echo "🚀 ANZX Marketing - Local Test Setup"
echo "===================================="
echo ""

# Check Node.js version
echo "📦 Checking Node.js version..."
NODE_VERSION=$(node -v)
echo "Node.js version: $NODE_VERSION"

NODE_MAJOR=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
if [ "$NODE_MAJOR" -lt 18 ]; then
    echo "❌ Error: Node.js 18+ is required"
    echo "Current version: $NODE_VERSION"
    exit 1
fi
echo "✅ Node.js version is compatible"
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating .env.local from example..."
    cp .env.local.example .env.local
    echo "✅ .env.local created"
    echo "⚠️  Please edit .env.local with your configuration"
else
    echo "✅ .env.local exists"
fi
echo ""

# Run type check
echo "🔍 Running TypeScript type check..."
if npm run type-check; then
    echo "✅ No TypeScript errors"
else
    echo "⚠️  TypeScript errors found (non-blocking)"
fi
echo ""

# Check for common issues
echo "🔍 Checking for common issues..."

# Check if messages files exist
if [ -f "messages/en.json" ] && [ -f "messages/hi.json" ]; then
    echo "✅ Translation files exist"
else
    echo "❌ Missing translation files"
    exit 1
fi

# Check if i18n.ts exists
if [ -f "i18n.ts" ]; then
    echo "✅ i18n configuration exists"
else
    echo "❌ Missing i18n.ts"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Review .env.local and add any required API keys"
echo "2. Run: npm run dev"
echo "3. Open: http://localhost:3000"
echo ""
echo "📚 For more information, see LOCAL_TESTING_GUIDE.md"
