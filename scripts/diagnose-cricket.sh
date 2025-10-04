#!/bin/bash
set -euo pipefail

echo "🏏 Cricket Chatbot Deep Diagnostic"
echo "===================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}1. Testing Cricket Page Response${NC}"
echo "-----------------------------------"

echo "Fetching https://anzx.ai/cricket..."
CRICKET_HTML=$(curl -s https://anzx.ai/cricket)

echo -n "✓ HTTP Status: "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://anzx.ai/cricket)
echo "$STATUS"

echo -n "✓ Content-Type: "
curl -sI https://anzx.ai/cricket | grep -i "content-type" || echo "Not found"

echo ""
echo -e "${BLUE}2. Checking HTML Structure${NC}"
echo "---------------------------"

echo -n "✓ Has DOCTYPE: "
if echo "$CRICKET_HTML" | grep -q "<!DOCTYPE html>"; then
  echo -e "${GREEN}YES${NC}"
else
  echo -e "${RED}NO${NC}"
fi

echo -n "✓ Has <html> tag: "
if echo "$CRICKET_HTML" | grep -q "<html"; then
  echo -e "${GREEN}YES${NC}"
else
  echo -e "${RED}NO${NC}"
fi

echo -n "✓ Has <body> tag: "
if echo "$CRICKET_HTML" | grep -q "<body"; then
  echo -e "${GREEN}YES${NC}"
else
  echo -e "${RED}NO${NC}"
fi

echo -n "✓ Has error marker (__next_error__): "
if echo "$CRICKET_HTML" | grep -q "__next_error__"; then
  echo -e "${RED}YES${NC} - This is the problem!"
else
  echo -e "${GREEN}NO${NC}"
fi

echo ""
echo -e "${BLUE}3. Checking for Cricket Content${NC}"
echo "--------------------------------"

echo -n "✓ Contains 'cricket': "
CRICKET_COUNT=$(echo "$CRICKET_HTML" | grep -io "cricket" | wc -l)
echo "$CRICKET_COUNT occurrences"

echo -n "✓ Contains 'chat': "
CHAT_COUNT=$(echo "$CRICKET_HTML" | grep -io "chat" | wc -l)
echo "$CHAT_COUNT occurrences"

echo -n "✓ Contains React components: "
if echo "$CRICKET_HTML" | grep -q "CricketChat\|ChatWidget\|ChatInterface"; then
  echo -e "${GREEN}YES${NC}"
else
  echo -e "${RED}NO${NC}"
fi

echo ""
echo -e "${BLUE}4. Checking JavaScript Bundles${NC}"
echo "-------------------------------"

echo -n "✓ Next.js scripts present: "
if echo "$CRICKET_HTML" | grep -q "_next/static"; then
  echo -e "${GREEN}YES${NC}"
else
  echo -e "${RED}NO${NC}"
fi

echo -n "✓ Main app bundle: "
if echo "$CRICKET_HTML" | grep -q "main-app"; then
  echo -e "${GREEN}YES${NC}"
else
  echo -e "${RED}NO${NC}"
fi

echo ""
echo -e "${BLUE}5. Checking Worker Routing${NC}"
echo "---------------------------"

echo "Testing worker routing..."
echo -n "✓ Worker handling /cricket: "
HEADERS=$(curl -sI https://anzx.ai/cricket)
if echo "$HEADERS" | grep -qi "cf-ray"; then
  echo -e "${GREEN}YES${NC} (Cloudflare active)"
else
  echo -e "${RED}NO${NC}"
fi

echo ""
echo -e "${BLUE}6. Testing Direct Pages URL${NC}"
echo "----------------------------"

echo "Checking Cloudflare Pages deployment directly..."
CRICKET_CHATBOT_URL=$(gcloud secrets versions access latest --secret=CRICKET_CHATBOT_URL 2>/dev/null || echo "https://8b5618a8.anzx-cricket.pages.dev")
echo "Cricket Chatbot URL: $CRICKET_CHATBOT_URL"

echo -n "✓ Direct Pages URL status: "
PAGES_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$CRICKET_CHATBOT_URL" || echo "FAILED")
echo "$PAGES_STATUS"

if [ "$PAGES_STATUS" = "200" ]; then
  echo -n "✓ Direct Pages content: "
  PAGES_HTML=$(curl -s "$CRICKET_CHATBOT_URL")
  if echo "$PAGES_HTML" | grep -q "cricket"; then
    echo -e "${GREEN}HAS CRICKET CONTENT${NC}"
  else
    echo -e "${RED}NO CRICKET CONTENT${NC}"
  fi
fi

echo ""
echo -e "${BLUE}7. Checking for 404/Error Pages${NC}"
echo "--------------------------------"

echo -n "✓ Is it a 404 page: "
if echo "$CRICKET_HTML" | grep -q "404\|not found\|Page Not Found"; then
  echo -e "${RED}YES - Page not found!${NC}"
else
  echo -e "${GREEN}NO${NC}"
fi

echo ""
echo -e "${BLUE}8. HTML Preview (first 100 lines)${NC}"
echo "----------------------------------"
echo "$CRICKET_HTML" | head -100

echo ""
echo -e "${BLUE}9. Diagnosis Summary${NC}"
echo "--------------------"

if echo "$CRICKET_HTML" | grep -q "__next_error__"; then
  echo -e "${RED}❌ ISSUE FOUND: Page has __next_error__ marker${NC}"
  echo ""
  echo "Possible causes:"
  echo "1. Worker is not routing /cricket correctly"
  echo "2. Cricket chatbot deployment URL is wrong"
  echo "3. Cricket chatbot Pages project doesn't have content at root"
  echo "4. Worker is proxying to wrong URL"
  echo ""
  echo "Recommended fix:"
  echo "1. Check worker configuration (CRICKET_CHATBOT_URL)"
  echo "2. Verify cricket chatbot deployment exists"
  echo "3. Test direct Pages URL"
elif [ "$CRICKET_COUNT" -lt 1 ]; then
  echo -e "${RED}❌ ISSUE FOUND: No cricket content on page${NC}"
  echo ""
  echo "The page loads but has no cricket-related content."
  echo "This suggests the worker is not proxying correctly."
else
  echo -e "${GREEN}✅ Page appears to be working${NC}"
fi

echo ""
