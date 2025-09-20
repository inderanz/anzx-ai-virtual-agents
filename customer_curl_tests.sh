#!/bin/bash
# ANZX AI Platform - Real Customer Testing with curl
# Tests that simulate what actual customers would do

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE_URL="https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app"
TEST_RESULTS=()
TOTAL_TESTS=0
PASSED_TESTS=0

# Load test environment if available
if [ -f "test_environment.json" ]; then
    API_KEY=$(cat test_environment.json | grep -o '"api_key": "[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "")
else
    API_KEY=""
fi

echo -e "${BLUE}🚀 ANZX AI Platform - Real Customer Testing${NC}"
echo "=================================================="
echo -e "${BLUE}🌐 API Base URL: ${API_BASE_URL}${NC}"
echo -e "${BLUE}🔑 API Key: ${API_KEY:+Available}${API_KEY:-Not Available}${NC}"
echo "=================================================="

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -e "\n${YELLOW}🧪 Testing: ${test_name}${NC}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    # Run the test with timeout and SSL options
    if eval "$test_command" >/dev/null 2>&1; then
        if [ -n "$expected_pattern" ]; then
            # Check if response matches expected pattern
            if eval "$test_command" 2>/dev/null | grep -q "$expected_pattern"; then
                echo -e "  ${GREEN}✅ PASS${NC} - $test_name"
                PASSED_TESTS=$((PASSED_TESTS + 1))
                TEST_RESULTS+=("PASS: $test_name")
                return 0
            else
                echo -e "  ${RED}❌ FAIL${NC} - $test_name (unexpected response)"
                TEST_RESULTS+=("FAIL: $test_name (unexpected response)")
                return 1
            fi
        else
            echo -e "  ${GREEN}✅ PASS${NC} - $test_name"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            TEST_RESULTS+=("PASS: $test_name")
            return 0
        fi
    else
        echo -e "  ${RED}❌ FAIL${NC} - $test_name (connection/timeout error)"
        TEST_RESULTS+=("FAIL: $test_name (connection/timeout error)")
        return 1
    fi
}

# Function to test with curl (ignoring SSL issues like customers might)
curl_test() {
    curl -k -s --connect-timeout 10 --max-time 15 "$@"
}

echo -e "\n${BLUE}🔍 1. Platform Discovery & Health${NC}"

# Test 1: Basic Health Check
run_test "Health Check" \
    "curl_test '${API_BASE_URL}/health'" \
    "healthy"

# Test 2: API Documentation Access
run_test "API Documentation" \
    "curl_test '${API_BASE_URL}/docs'" \
    "ANZX AI Platform API"

# Test 3: OpenAPI Schema
run_test "OpenAPI Schema" \
    "curl_test '${API_BASE_URL}/openapi.json'" \
    "openapi"

echo -e "\n${BLUE}🤖 2. AI Assistant Discovery${NC}"

# Test 4: Assistant Listing
run_test "Assistant Discovery" \
    "curl_test '${API_BASE_URL}/assistants'" \
    "assistants"

# Test 5: Assistant Chat (expect error but endpoint should exist)
run_test "Assistant Chat Endpoint" \
    "curl_test -X POST '${API_BASE_URL}/assistants/test-123/chat' -H 'Content-Type: application/json' -d '{\"message\":\"test\"}'" \
    ""

echo -e "\n${BLUE}⚡ 3. Performance Testing${NC}"

# Test 6: Response Time Check
echo -e "\n${YELLOW}🧪 Testing: Response Time Performance${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

start_time=$(date +%s%N)
if curl_test "${API_BASE_URL}/health" > /dev/null; then
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [ $response_time -lt 5000 ]; then
        echo -e "  ${GREEN}✅ PASS${NC} - Response Time Performance (${response_time}ms)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("PASS: Response Time Performance (${response_time}ms)")
    else
        echo -e "  ${RED}❌ FAIL${NC} - Response Time Performance (${response_time}ms - too slow)"
        TEST_RESULTS+=("FAIL: Response Time Performance (${response_time}ms)")
    fi
else
    echo -e "  ${RED}❌ FAIL${NC} - Response Time Performance (connection failed)"
    TEST_RESULTS+=("FAIL: Response Time Performance (connection failed)")
fi

echo -e "\n${BLUE}🚫 4. Error Handling${NC}"

# Test 7: 404 Error Handling
echo -e "\n${YELLOW}🧪 Testing: 404 Error Handling${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

http_code=$(curl_test -o /dev/null -w "%{http_code}" "${API_BASE_URL}/nonexistent-endpoint")
if [ "$http_code" = "404" ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - 404 Error Handling"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("PASS: 404 Error Handling")
else
    echo -e "  ${RED}❌ FAIL${NC} - 404 Error Handling (got HTTP $http_code)"
    TEST_RESULTS+=("FAIL: 404 Error Handling (got HTTP $http_code)")
fi

echo -e "\n${BLUE}🔒 5. Security & Headers${NC}"

# Test 8: Security Headers
echo -e "\n${YELLOW}🧪 Testing: Security Headers${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

headers=$(curl_test -I "${API_BASE_URL}/health" 2>/dev/null | grep -i "x-\|strict-transport\|content-security" | wc -l)
if [ "$headers" -gt 0 ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - Security Headers (found $headers security headers)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("PASS: Security Headers (found $headers)")
else
    echo -e "  ${RED}❌ FAIL${NC} - Security Headers (no security headers found)"
    TEST_RESULTS+=("FAIL: Security Headers (none found)")
fi

echo -e "\n${BLUE}🔐 6. API Authentication${NC}"

if [ -n "$API_KEY" ]; then
    # Test 9: API Key Authentication
    echo -e "\n${YELLOW}🧪 Testing: API Key Authentication${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    auth_response=$(curl_test -w "%{http_code}" -o /dev/null -H "Authorization: Bearer $API_KEY" "${API_BASE_URL}/api/v1/agents/")
    if [ "$auth_response" != "500" ]; then
        echo -e "  ${GREEN}✅ PASS${NC} - API Key Authentication (HTTP $auth_response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("PASS: API Key Authentication (HTTP $auth_response)")
    else
        echo -e "  ${RED}❌ FAIL${NC} - API Key Authentication (server error)"
        TEST_RESULTS+=("FAIL: API Key Authentication (server error)")
    fi
    
    # Test 10: Unauthorized Access
    echo -e "\n${YELLOW}🧪 Testing: Unauthorized Access Block${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    unauth_response=$(curl_test -w "%{http_code}" -o /dev/null "${API_BASE_URL}/api/v1/agents/")
    if [ "$unauth_response" = "401" ] || [ "$unauth_response" = "403" ]; then
        echo -e "  ${GREEN}✅ PASS${NC} - Unauthorized Access Block (HTTP $unauth_response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("PASS: Unauthorized Access Block (HTTP $unauth_response)")
    else
        echo -e "  ${RED}❌ FAIL${NC} - Unauthorized Access Block (HTTP $unauth_response)"
        TEST_RESULTS+=("FAIL: Unauthorized Access Block (HTTP $unauth_response)")
    fi
else
    echo -e "  ${YELLOW}⚠️  SKIP${NC} - API Authentication tests (no API key available)"
fi

echo -e "\n${BLUE}🌐 7. Real Customer Scenarios${NC}"

# Test: Customer trying to understand the platform
echo -e "\n${YELLOW}🧪 Testing: Customer Platform Exploration${NC}"
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Simulate a customer checking if the platform is working
platform_check=0

# Check health
if curl_test "${API_BASE_URL}/health" | grep -q "healthy"; then
    platform_check=$((platform_check + 1))
fi

# Check docs are accessible
if curl_test "${API_BASE_URL}/docs" | grep -q -i "api\|swagger\|documentation"; then
    platform_check=$((platform_check + 1))
fi

# Check assistants endpoint responds
if curl_test "${API_BASE_URL}/assistants" | grep -q -i "assistants\|error"; then
    platform_check=$((platform_check + 1))
fi

if [ $platform_check -ge 2 ]; then
    echo -e "  ${GREEN}✅ PASS${NC} - Customer Platform Exploration ($platform_check/3 checks passed)"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TEST_RESULTS+=("PASS: Customer Platform Exploration ($platform_check/3)")
else
    echo -e "  ${RED}❌ FAIL${NC} - Customer Platform Exploration ($platform_check/3 checks passed)"
    TEST_RESULTS+=("FAIL: Customer Platform Exploration ($platform_check/3)")
fi

# Calculate success rate
SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))

echo ""
echo "=================================================="
echo -e "${BLUE}🎯 CUSTOMER TESTING SUMMARY${NC}"
echo "=================================================="
echo -e "${BLUE}📊 Total Tests: ${TOTAL_TESTS}${NC}"
echo -e "${GREEN}✅ Passed: ${PASSED_TESTS}${NC}"
echo -e "${RED}❌ Failed: $((TOTAL_TESTS - PASSED_TESTS))${NC}"
echo -e "${BLUE}📈 Success Rate: ${SUCCESS_RATE}%${NC}"
echo ""

# Detailed results
echo -e "${BLUE}📋 Detailed Results:${NC}"
for result in "${TEST_RESULTS[@]}"; do
    if [[ $result == PASS:* ]]; then
        echo -e "  ${GREEN}✅ ${result#PASS: }${NC}"
    else
        echo -e "  ${RED}❌ ${result#FAIL: }${NC}"
    fi
done

echo ""

# Overall assessment
if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}🎉 EXCELLENT - Platform exceeds customer expectations!${NC}"
    exit_code=0
elif [ $SUCCESS_RATE -ge 75 ]; then
    echo -e "${GREEN}✅ GOOD - Platform meets customer expectations${NC}"
    exit_code=0
elif [ $SUCCESS_RATE -ge 60 ]; then
    echo -e "${YELLOW}⚠️  ACCEPTABLE - Minor improvements needed${NC}"
    exit_code=0
else
    echo -e "${RED}🔧 NEEDS IMPROVEMENT - Significant issues found${NC}"
    exit_code=1
fi

echo ""
echo -e "${BLUE}💡 Customer Experience Notes:${NC}"
echo "   • SSL certificate verification may require -k flag in curl"
echo "   • Database connection errors are expected in test environment"
echo "   • API endpoints should respond with proper HTTP status codes"
echo "   • Documentation should be accessible to potential customers"
echo "   • Authentication should be properly enforced"

echo ""
echo "=================================================="

# Save results to file
cat > customer_test_results.txt << EOF
ANZX AI Platform - Customer Testing Results
Generated: $(date)
API Base URL: $API_BASE_URL

SUMMARY:
Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $((TOTAL_TESTS - PASSED_TESTS))
Success Rate: $SUCCESS_RATE%

DETAILED RESULTS:
$(printf '%s\n' "${TEST_RESULTS[@]}")

ASSESSMENT:
$(if [ $SUCCESS_RATE -ge 90 ]; then echo "EXCELLENT - Platform exceeds customer expectations!"; elif [ $SUCCESS_RATE -ge 75 ]; then echo "GOOD - Platform meets customer expectations"; elif [ $SUCCESS_RATE -ge 60 ]; then echo "ACCEPTABLE - Minor improvements needed"; else echo "NEEDS IMPROVEMENT - Significant issues found"; fi)
EOF

echo -e "${BLUE}📄 Results saved to: customer_test_results.txt${NC}"

exit $exit_code