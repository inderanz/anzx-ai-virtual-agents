#!/bin/bash
set -euo pipefail

echo "🏏 Checking Cricket Chatbot Status"
echo "===================================="
echo ""

echo "1. Testing direct Pages URL..."
echo "URL: https://d1e8b1c8.anzx-cricket.pages.dev/"
curl -sI https://d1e8b1c8.anzx-cricket.pages.dev/ | head -3
echo ""

echo "2. Testing via anzx.ai/cricket..."
echo "URL: https://anzx.ai/cricket"
curl -sI https://anzx.ai/cricket 2>&1 | head -5
echo ""

echo "3. Checking for BAILOUT error..."
CRICKET_HTML=$(curl -s https://anzx.ai/cricket 2>&1)
if echo "$CRICKET_HTML" | grep -q "BAILOUT_TO_CLIENT_SIDE_RENDERING"; then
  echo "❌ BAILOUT error still present"
else
  echo "✅ No BAILOUT error"
fi

echo ""
echo "4. Checking for cricket content..."
CRICKET_COUNT=$(echo "$CRICKET_HTML" | grep -io "cricket" | wc -l | tr -d ' ')
echo "Cricket mentions: $CRICKET_COUNT"

echo ""
echo "5. Checking HTML structure..."
if echo "$CRICKET_HTML" | grep -q "<html"; then
  echo "✅ Has HTML structure"
else
  echo "❌ No HTML structure"
fi

echo ""
echo "6. First 50 lines of HTML:"
echo "$CRICKET_HTML" | head -50
