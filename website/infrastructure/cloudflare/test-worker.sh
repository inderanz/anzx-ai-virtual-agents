#!/bin/bash
# Test script for Cloudflare Worker deployment
# Validates that the Worker is properly proxying requests to cricket-agent

set -euo pipefail

# Configuration
DOMAIN="${1:-anzx.ai}"
API_BASE="https://${DOMAIN}/api/cricket"

echo "Testing Cloudflare Worker at ${API_BASE}"

# Test 1: Health check
echo "1. Testing health check..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/healthz")
if [[ "$HEALTH_RESPONSE" == "200" ]]; then
    echo "✅ Health check passed (${HEALTH_RESPONSE})"
else
    echo "❌ Health check failed (${HEALTH_RESPONSE})"
    exit 1
fi

# Test 2: CORS preflight
echo "2. Testing CORS preflight..."
CORS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X OPTIONS \
    -H "Origin: https://${DOMAIN}" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    "${API_BASE}/v1/ask")
if [[ "$CORS_RESPONSE" == "204" ]]; then
    echo "✅ CORS preflight passed (${CORS_RESPONSE})"
else
    echo "❌ CORS preflight failed (${CORS_RESPONSE})"
    exit 1
fi

# Test 3: Cricket query
echo "3. Testing cricket query..."
CRICKET_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/ask" \
    -H "Content-Type: application/json" \
    -H "Origin: https://${DOMAIN}" \
    -d '{"text":"Show me the fixtures for Caroline Springs", "source":"web"}')
if echo "$CRICKET_RESPONSE" | jq -e '.answer' > /dev/null 2>&1; then
    echo "✅ Cricket query passed"
    echo "Response: $(echo "$CRICKET_RESPONSE" | jq -r '.answer' | head -c 100)..."
else
    echo "❌ Cricket query failed"
    echo "Response: $CRICKET_RESPONSE"
    exit 1
fi

# Test 4: CORS headers
echo "4. Testing CORS headers..."
CORS_HEADERS=$(curl -s -I "${API_BASE}/healthz" | grep -i "access-control-allow-origin")
if echo "$CORS_HEADERS" | grep -q "https://${DOMAIN}"; then
    echo "✅ CORS headers present"
else
    echo "❌ CORS headers missing or incorrect"
    echo "Headers: $CORS_HEADERS"
    exit 1
fi

echo ""
echo "🎉 All Cloudflare Worker tests passed!"
echo "Worker is properly proxying requests to cricket-agent"
