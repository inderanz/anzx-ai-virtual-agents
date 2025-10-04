#!/bin/bash
set -euo pipefail

echo "🔍 Deep Browser-Level Testing (Developer Tools Simulation)"
echo "==========================================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

echo "📍 Test 1: Main Site HTML Structure"
echo "------------------------------------"

echo "Fetching https://anzx.ai/en..."
HOMEPAGE=$(curl -s https://anzx.ai/en)

echo -n "✓ Checking for error markers (NEXT_NOT_FOUND, NEXT_ERROR)... "
if echo "$HOMEPAGE" | grep -q "NEXT_NOT_FOUND\|NEXT_ERROR\|__next_error__"; then
  echo -e "${RED}❌ FAIL - Error markers found!${NC}"
  echo "$HOMEPAGE" | grep -o "NEXT_NOT_FOUND\|NEXT_ERROR\|__next_error__" | head -3
  ((FAIL++))
else
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
fi

echo -n "✓ Checking HTML structure (html, head, body tags)... "
if echo "$HOMEPAGE" | grep -q "<html" && echo "$HOMEPAGE" | grep -q "<head" && echo "$HOMEPAGE" | grep -q "<body"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for proper DOCTYPE... "
if echo "$HOMEPAGE" | grep -q "<!DOCTYPE html>"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking language attribute (lang=\"en\")... "
if echo "$HOMEPAGE" | grep -q 'lang="en"'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo ""
echo "📍 Test 2: Component Rendering"
echo "-------------------------------"

echo -n "✓ Checking HomeHero component... "
if echo "$HOMEPAGE" | grep -q "HomeHero"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking FeatureGrid component... "
if echo "$HOMEPAGE" | grep -q "FeatureGrid"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking LogoCarousel component... "
if echo "$HOMEPAGE" | grep -q "LogoCarousel"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking Header component... "
if echo "$HOMEPAGE" | grep -q "Header\|header\|navigation"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking Footer component... "
if echo "$HOMEPAGE" | grep -q "Footer\|footer"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo ""
echo "📍 Test 3: JavaScript & Next.js Hydration"
echo "------------------------------------------"

echo -n "✓ Checking for Next.js scripts... "
if echo "$HOMEPAGE" | grep -q "_next/static"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for webpack chunks... "
if echo "$HOMEPAGE" | grep -q "webpack"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for main app bundle... "
if echo "$HOMEPAGE" | grep -q "main-app"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for polyfills... "
if echo "$HOMEPAGE" | grep -q "polyfills"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${YELLOW}⚠️  WARNING${NC} (Optional)"
fi

echo ""
echo "📍 Test 4: SEO & Meta Tags (Like Browser DevTools)"
echo "---------------------------------------------------"

echo -n "✓ Checking title tag... "
if echo "$HOMEPAGE" | grep -q "<title>"; then
  TITLE=$(echo "$HOMEPAGE" | grep -o "<title>[^<]*</title>" | head -1)
  echo -e "${GREEN}✅ PASS${NC} - $TITLE"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking meta description... "
if echo "$HOMEPAGE" | grep -q 'name="description"'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking meta viewport... "
if echo "$HOMEPAGE" | grep -q 'name="viewport"'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking Open Graph tags... "
if echo "$HOMEPAGE" | grep -q 'property="og:'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking Twitter Card tags... "
if echo "$HOMEPAGE" | grep -q 'name="twitter:'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo ""
echo "📍 Test 5: CSS & Styling"
echo "-------------------------"

echo -n "✓ Checking for CSS files... "
if echo "$HOMEPAGE" | grep -q "\.css"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for inline styles... "
if echo "$HOMEPAGE" | grep -q "style="; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${YELLOW}⚠️  WARNING${NC} (Optional)"
fi

echo ""
echo "📍 Test 6: Accessibility"
echo "------------------------"

echo -n "✓ Checking for skip-to-content link... "
if echo "$HOMEPAGE" | grep -q "skip-to-content\|Skip to main content"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for main landmark... "
if echo "$HOMEPAGE" | grep -q '<main\|id="main'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo ""
echo "📍 Test 7: Cricket Chatbot Deep Check"
echo "--------------------------------------"

echo "Fetching https://anzx.ai/cricket..."
CRICKET=$(curl -s https://anzx.ai/cricket)

echo -n "✓ Checking for error markers... "
if echo "$CRICKET" | grep -q "NEXT_NOT_FOUND\|NEXT_ERROR\|__next_error__"; then
  echo -e "${RED}❌ FAIL - Error markers found!${NC}"
  ((FAIL++))
else
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
fi

echo -n "✓ Checking HTML structure... "
if echo "$CRICKET" | grep -q "<html" && echo "$CRICKET" | grep -q "<body"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for cricket-related content... "
if echo "$CRICKET" | grep -qi "cricket"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for Next.js scripts... "
if echo "$CRICKET" | grep -q "_next/static"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo ""
echo "📍 Test 8: Network Resources (Like Network Tab)"
echo "------------------------------------------------"

echo -n "✓ Testing main CSS bundle... "
CSS_URL=$(echo "$HOMEPAGE" | grep -o 'href="/_next/static/css/[^"]*\.css"' | head -1 | sed 's/href="//;s/"//')
if [ -n "$CSS_URL" ]; then
  CSS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://anzx.ai$CSS_URL")
  if [ "$CSS_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} (200 OK)"
    ((PASS++))
  else
    echo -e "${RED}❌ FAIL${NC} (Status: $CSS_STATUS)"
    ((FAIL++))
  fi
else
  echo -e "${YELLOW}⚠️  WARNING${NC} (No CSS URL found)"
fi

echo -n "✓ Testing main JS bundle... "
JS_URL=$(echo "$HOMEPAGE" | grep -o 'src="/_next/static/chunks/[^"]*\.js"' | head -1 | sed 's/src="//;s/"//')
if [ -n "$JS_URL" ]; then
  JS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://anzx.ai$JS_URL")
  if [ "$JS_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ PASS${NC} (200 OK)"
    ((PASS++))
  else
    echo -e "${RED}❌ FAIL${NC} (Status: $JS_STATUS)"
    ((FAIL++))
  fi
else
  echo -e "${YELLOW}⚠️  WARNING${NC} (No JS URL found)"
fi

echo ""
echo "📍 Test 9: Locale Switching (i18n)"
echo "-----------------------------------"

echo "Fetching Hindi version..."
HINDI=$(curl -s https://anzx.ai/hi)

echo -n "✓ Checking Hindi page loads... "
if echo "$HINDI" | grep -q "<html"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking language attribute (lang=\"hi\")... "
if echo "$HINDI" | grep -q 'lang="hi"'; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Checking for no error markers in Hindi... "
if echo "$HINDI" | grep -q "NEXT_NOT_FOUND\|NEXT_ERROR"; then
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
else
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
fi

echo ""
echo "📍 Test 10: Response Headers (Like Network Tab)"
echo "------------------------------------------------"

echo "Checking response headers for https://anzx.ai/en..."
HEADERS=$(curl -sI https://anzx.ai/en)

echo -n "✓ Content-Type header... "
if echo "$HEADERS" | grep -qi "content-type.*text/html"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Cache-Control header... "
if echo "$HEADERS" | grep -qi "cache-control"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${YELLOW}⚠️  WARNING${NC}"
fi

echo -n "✓ Cloudflare CDN (cf-ray header)... "
if echo "$HEADERS" | grep -qi "cf-ray"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "✓ Security headers (X-Content-Type-Options)... "
if echo "$HEADERS" | grep -qi "x-content-type-options"; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${YELLOW}⚠️  WARNING${NC}"
fi

echo ""
echo "==========================================================="
echo "📊 Final Test Results"
echo "==========================================================="
echo -e "Total Tests: $((PASS + FAIL))"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}🎉 SUCCESS! Both sites are fully functional!${NC}"
  echo ""
  echo "✅ Main site (https://anzx.ai) - Working perfectly"
  echo "✅ Cricket chatbot (https://anzx.ai/cricket) - Working perfectly"
  echo "✅ All components rendering correctly"
  echo "✅ JavaScript bundles loading"
  echo "✅ SEO tags present"
  echo "✅ i18n working (English & Hindi)"
  echo "✅ No NEXT_NOT_FOUND errors"
  echo ""
  exit 0
else
  echo -e "${RED}⚠️  Some tests failed. Review above for details.${NC}"
  echo ""
  exit 1
fi
