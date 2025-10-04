#!/bin/bash
set -euo pipefail

echo "🧪 Comprehensive Production Site Testing"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

test_url() {
  local url=$1
  local description=$2
  local expected_content=$3
  
  echo -n "Testing: $description... "
  
  # Get HTTP status
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  
  if [ "$status" = "200" ]; then
    # Check content if provided
    if [ -n "$expected_content" ]; then
      content=$(curl -s "$url")
      if echo "$content" | grep -q "$expected_content"; then
        echo -e "${GREEN}✅ PASS${NC} (200 OK, content found)"
        ((PASS++))
        return 0
      else
        echo -e "${RED}❌ FAIL${NC} (200 OK, but content missing: $expected_content)"
        ((FAIL++))
        return 1
      fi
    else
      echo -e "${GREEN}✅ PASS${NC} (200 OK)"
      ((PASS++))
      return 0
    fi
  else
    echo -e "${RED}❌ FAIL${NC} (Status: $status)"
    ((FAIL++))
    return 1
  fi
}

echo "📍 Testing Main Site (https://anzx.ai)"
echo "----------------------------------------"

# Test root redirect
test_url "https://anzx.ai" "Root page" ""

# Test English homepage
test_url "https://anzx.ai/en" "English homepage" "HomeHero"

# Test Hindi homepage
test_url "https://anzx.ai/hi" "Hindi homepage" ""

# Test key pages
test_url "https://anzx.ai/en/agentic-ai" "Agentic AI page" "agentic"
test_url "https://anzx.ai/en/ai-agents-australia" "Australia page" "Australia"
test_url "https://anzx.ai/en/ai-agents-india" "India page" "India"
test_url "https://anzx.ai/en/ai-agents-singapore" "Singapore page" "Singapore"
test_url "https://anzx.ai/en/customer-service-ai" "Customer Service AI" "customer"
test_url "https://anzx.ai/en/ai-sales-agent" "AI Sales Agent" "sales"
test_url "https://anzx.ai/en/ai-interviewer" "AI Interviewer" "interview"
test_url "https://anzx.ai/en/workflow-automation" "Workflow Automation" "workflow"
test_url "https://anzx.ai/en/what-is-an-ai-agent" "What is AI Agent" "agent"

# Test blog
test_url "https://anzx.ai/en/blog" "Blog listing" "blog"
test_url "https://anzx.ai/en/blog/ai-implementation-guide" "Blog post" ""

echo ""
echo "📍 Testing Cricket Chatbot (https://anzx.ai/cricket)"
echo "-----------------------------------------------------"

# Test cricket chatbot
test_url "https://anzx.ai/cricket" "Cricket chatbot page" ""

echo ""
echo "📍 Testing Static Assets"
echo "-------------------------"

# Test static assets
test_url "https://anzx.ai/favicon.ico" "Favicon" ""
test_url "https://anzx.ai/_next/static/css" "CSS assets" "" || echo -e "${YELLOW}⚠️  CSS check skipped${NC}"

echo ""
echo "📍 Testing Locale Switching"
echo "----------------------------"

# Test locale switching
test_url "https://anzx.ai/en" "English locale" ""
test_url "https://anzx.ai/hi" "Hindi locale" ""
test_url "https://anzx.ai/en/agentic-ai" "English page" ""
test_url "https://anzx.ai/hi/agentic-ai" "Hindi page" ""

echo ""
echo "📍 Testing SEO & Meta Tags"
echo "---------------------------"

echo -n "Checking meta tags on homepage... "
meta_content=$(curl -s "https://anzx.ai/en" | grep -o '<meta.*description' | head -1)
if [ -n "$meta_content" ]; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo -n "Checking Open Graph tags... "
og_content=$(curl -s "https://anzx.ai/en" | grep -o 'og:title\|og:description' | head -1)
if [ -n "$og_content" ]; then
  echo -e "${GREEN}✅ PASS${NC}"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC}"
  ((FAIL++))
fi

echo ""
echo "📍 Testing Performance Headers"
echo "-------------------------------"

echo -n "Checking cache headers... "
cache_header=$(curl -sI "https://anzx.ai/en" | grep -i "cache-control")
if [ -n "$cache_header" ]; then
  echo -e "${GREEN}✅ PASS${NC} ($cache_header)"
  ((PASS++))
else
  echo -e "${YELLOW}⚠️  WARNING${NC} (No cache headers)"
fi

echo -n "Checking CDN headers... "
cdn_header=$(curl -sI "https://anzx.ai/en" | grep -i "cf-ray")
if [ -n "$cdn_header" ]; then
  echo -e "${GREEN}✅ PASS${NC} (Cloudflare CDN active)"
  ((PASS++))
else
  echo -e "${RED}❌ FAIL${NC} (No CDN headers)"
  ((FAIL++))
fi

echo ""
echo "📍 Testing Error Pages"
echo "----------------------"

echo -n "Testing 404 page... "
status_404=$(curl -s -o /dev/null -w "%{http_code}" "https://anzx.ai/en/nonexistent-page")
if [ "$status_404" = "404" ]; then
  echo -e "${GREEN}✅ PASS${NC} (404 returned correctly)"
  ((PASS++))
else
  echo -e "${YELLOW}⚠️  WARNING${NC} (Status: $status_404)"
fi

echo ""
echo "========================================"
echo "📊 Test Results Summary"
echo "========================================"
echo -e "Total Tests: $((PASS + FAIL))"
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
  echo -e "${GREEN}🎉 All tests passed! Both sites are working correctly.${NC}"
  exit 0
else
  echo -e "${RED}⚠️  Some tests failed. Please review the results above.${NC}"
  exit 1
fi
