#!/bin/bash

echo "🧪 Testing ANZX Marketing Website Locally"
echo "=========================================="
echo ""

# Wait for server to be ready
echo "⏳ Waiting for server to start..."
sleep 5

# Test homepage
echo "✅ Testing homepage (/)..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/

# Test English homepage
echo "✅ Testing English homepage (/en)..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/en

# Test Hindi homepage
echo "✅ Testing Hindi homepage (/hi)..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/hi

# Test product pages
echo "✅ Testing AI Interviewer page..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/ai-interviewer

echo "✅ Testing Customer Service AI page..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/customer-service-ai

echo "✅ Testing AI Sales Agent page..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000/ai-sales-agent

echo ""
echo "🎉 Local testing complete!"
echo ""
echo "📝 To view the site, open: http://localhost:3000"
echo "🛑 To stop the server: pkill -f 'next dev'"
