#!/bin/bash

echo "🚀 Starting ANZX Marketing Development Server..."
echo ""
echo "The server will start on: http://localhost:3000"
echo ""
echo "📍 Test these URLs once the server starts:"
echo "   - Homepage: http://localhost:3000/en"
echo "   - Hindi: http://localhost:3000/hi"
echo "   - AI Interviewer: http://localhost:3000/en/ai-interviewer"
echo "   - Blog: http://localhost:3000/en/blog"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "Starting in 3 seconds..."
sleep 3

npm run dev
