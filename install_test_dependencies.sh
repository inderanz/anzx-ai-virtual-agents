#!/bin/bash
# Install all dependencies for testing

echo "📦 Installing Python dependencies..."
pip3 install -r requirements-test.txt

echo "📦 Installing Node.js dependencies..."
npm init -y
npm install @playwright/test
npx playwright install

echo "✅ All dependencies installed!"
echo "Next steps:"
echo "1. Run: ./connect_to_db.sh (in another terminal)"
echo "2. Run: python3 setup_test_database.py"
echo "3. Run: npx playwright test"
