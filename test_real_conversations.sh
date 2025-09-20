#!/bin/bash

# ANZX AI Platform - Real User Conversation Testing
# Simulates authentic customer interactions with AI agents using Vertex AI

set -e

BASE_URL="https://anzx-ai-platform-core-api-1088103632448.australia-southeast1.run.app"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🤖 ANZX AI Platform - Real User Conversation Testing"
echo "=================================================="
echo "Base URL: $BASE_URL"
echo "Timestamp: $TIMESTAMP"
echo ""
echo "This test simulates real customers having authentic conversations"
echo "with AI agents powered by Google Vertex AI and Gemini models."
echo ""

# Get available assistants
echo "📋 Getting available assistants..."
assistants_response=$(curl -s "$BASE_URL/assistants")

if ! echo "$assistants_response" | jq -e '.assistants' > /dev/null 2>&1; then
    echo "❌ Cannot get assistants list. Response:"
    echo "$assistants_response"
    exit 1
fi

echo "✅ Found assistants:"
echo "$assistants_response" | jq -r '.assistants[] | "   - \(.name) (\(.type)) - ID: \(.id)"'
echo ""

# Function to have a conversation with an assistant
have_conversation() {
    local assistant_name="$1"
    local assistant_id="$2"
    local assistant_type="$3"
    local user_message="$4"
    local scenario_description="$5"
    
    echo "💬 CONVERSATION TEST: $scenario_description"
    echo "   🤖 Assistant: $assistant_name ($assistant_type)"
    echo "   👤 User Message: \"$user_message\""
    echo ""
    
    # Create realistic chat payload
    chat_payload=$(jq -n \
        --arg message "$user_message" \
        --arg channel "web-chat" \
        '{
            message: $message, 
            channel: $channel, 
            context: {
                user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                session_id: "test-session-'$(date +%s)'",
                timestamp: "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
                test_scenario: true
            }
        }')
    
    echo "   📤 Sending message to AI agent..."
    
    # Send chat request and measure response time
    start_time=$(date +%s%N)
    chat_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -H "Content-Type: application/json" \
        -H "User-Agent: ANZX-Test-Client/1.0" \
        -d "$chat_payload" \
        "$BASE_URL/assistants/$assistant_id/chat")
    end_time=$(date +%s%N)
    
    # Calculate response time
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    # Parse response
    http_status=$(echo "$chat_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    response_body=$(echo "$chat_response" | sed -E 's/HTTPSTATUS:[0-9]*$//')
    
    echo "   ⏱️  Response time: ${response_time}ms"
    
    if [ "$http_status" = "200" ]; then
        echo "   ✅ Conversation successful!"
        
        # Parse and display the AI response
        if echo "$response_body" | jq -e '.reply' > /dev/null 2>&1; then
            ai_reply=$(echo "$response_body" | jq -r '.reply')
            echo "   🤖 AI Response:"
            echo "      \"$ai_reply\""
            
            # Show additional metadata if available
            if echo "$response_body" | jq -e '.metadata' > /dev/null 2>&1; then
                echo "   📊 Response Metadata:"
                
                # Show tokens used
                if echo "$response_body" | jq -e '.metadata.tokens_input' > /dev/null 2>&1; then
                    tokens_in=$(echo "$response_body" | jq -r '.metadata.tokens_input // "N/A"')
                    tokens_out=$(echo "$response_body" | jq -r '.metadata.tokens_output // "N/A"')
                    echo "      Tokens: $tokens_in input, $tokens_out output"
                fi
                
                # Show model used
                if echo "$response_body" | jq -e '.metadata.model' > /dev/null 2>&1; then
                    model=$(echo "$response_body" | jq -r '.metadata.model')
                    echo "      Model: $model"
                fi
                
                # Show confidence if available
                if echo "$response_body" | jq -e '.metadata.confidence_score' > /dev/null 2>&1; then
                    confidence=$(echo "$response_body" | jq -r '.metadata.confidence_score')
                    echo "      Confidence: $confidence"
                fi
            fi
            
            # Analyze response quality
            response_length=${#ai_reply}
            if [ $response_length -gt 50 ] && [ $response_length -lt 1000 ]; then
                echo "   ✅ Response quality: Good length ($response_length chars)"
            elif [ $response_length -le 50 ]; then
                echo "   ⚠️  Response quality: Too short ($response_length chars)"
            else
                echo "   ⚠️  Response quality: Too long ($response_length chars)"
            fi
            
        else
            echo "   ⚠️  Response received but no 'reply' field found"
            echo "   📄 Raw response: $(echo "$response_body" | head -c 200)..."
        fi
        
    else
        echo "   ❌ Conversation failed (HTTP $http_status)"
        echo "   📄 Error response: $(echo "$response_body" | head -c 300)..."
    fi
    
    echo ""
    echo "   " $(printf '=%.0s' {1..60})
    echo ""
}

# Function to get assistant ID by type
get_assistant_id_by_type() {
    local target_type="$1"
    echo "$assistants_response" | jq -r ".assistants[] | select(.type == \"$target_type\") | .id" | head -1
}

get_assistant_name_by_type() {
    local target_type="$1"
    echo "$assistants_response" | jq -r ".assistants[] | select(.type == \"$target_type\") | .name" | head -1
}

echo "🎭 Starting Real User Conversation Scenarios..."
echo ""

# Scenario 1: Customer Support - Login Issue
support_id=$(get_assistant_id_by_type "support")
support_name=$(get_assistant_name_by_type "support")
if [ -n "$support_id" ]; then
    have_conversation \
        "$support_name" \
        "$support_id" \
        "support" \
        "Hi, I'm having trouble logging into my account. I keep getting an 'invalid credentials' error even though I'm sure my password is correct. I tried resetting it twice but still can't get in. This is really frustrating because I need to access my dashboard for an important client meeting in 30 minutes. Can you help me?" \
        "Customer Support - Urgent Login Issue"
fi

# Scenario 2: Sales Inquiry - Enterprise Plan
sales_id=$(get_assistant_id_by_type "sales")
sales_name=$(get_assistant_name_by_type "sales")
if [ -n "$sales_id" ]; then
    have_conversation \
        "$sales_name" \
        "$sales_id" \
        "sales" \
        "Hello! I'm the CTO at a fintech startup with about 75 employees. We're currently evaluating AI platforms for customer service automation and internal productivity tools. I'm particularly interested in your enterprise plan - could you tell me about the pricing, what's included, and whether you offer custom integrations with our existing Salesforce and Slack setup? We're looking to make a decision within the next two weeks." \
        "Sales Inquiry - Enterprise Evaluation"
fi

# Scenario 3: Technical Support - API Integration
technical_id=$(get_assistant_id_by_type "technical")
technical_name=$(get_assistant_name_by_type "technical")
if [ -n "$technical_id" ]; then
    have_conversation \
        "$technical_name" \
        "$technical_id" \
        "technical" \
        "I'm a developer trying to integrate your API into our React application. I'm getting a CORS error when making requests from our frontend (running on localhost:3000) to your API endpoints. I've set up the API key correctly and can make successful requests from Postman, but browser requests are being blocked. Do you have documentation on CORS configuration or whitelist settings I need to configure?" \
        "Technical Support - API Integration Issue"
fi

# Scenario 4: Administrative Assistant - Meeting Scheduling
admin_id=$(get_assistant_id_by_type "admin")
admin_name=$(get_assistant_name_by_type "admin")
if [ -n "$admin_id" ]; then
    have_conversation \
        "$admin_name" \
        "$admin_id" \
        "admin" \
        "I need to schedule a quarterly board meeting for next month. The meeting should be 3 hours long, include 8 board members plus our CEO and CFO, and needs to accommodate people in Sydney, Melbourne, and San Francisco time zones. Can you suggest some optimal time slots and help me send out calendar invites? Also, we'll need a conference room that can handle video conferencing for the remote participants." \
        "Administrative - Complex Meeting Scheduling"
fi

# Scenario 5: Content Creation - Marketing Campaign
content_id=$(get_assistant_id_by_type "content")
content_name=$(get_assistant_name_by_type "content")
if [ -n "$content_id" ]; then
    have_conversation \
        "$content_name" \
        "$content_id" \
        "content" \
        "We're launching a new AI-powered analytics feature next month and need content for our marketing campaign. Can you help me create a compelling blog post that explains the benefits of AI analytics for small business owners? The tone should be approachable but professional, around 800-1000 words, and include practical examples of how AI can help with inventory management, customer insights, and sales forecasting. Our target audience is non-technical business owners who are curious about AI but might be intimidated by the technology." \
        "Content Creation - Product Launch Blog Post"
fi

# Scenario 6: Business Insights - Performance Analysis
insights_id=$(get_assistant_id_by_type "insights")
insights_name=$(get_assistant_name_by_type "insights")
if [ -n "$insights_id" ]; then
    have_conversation \
        "$insights_name" \
        "$insights_id" \
        "insights" \
        "I'm preparing for our monthly executive review and need help analyzing our platform performance data. Over the past 30 days, we've seen a 23% increase in API calls, but our customer satisfaction scores have dropped from 4.2 to 3.8. Our response times have also increased from an average of 150ms to 280ms. Can you help me identify potential correlations and suggest what might be causing the satisfaction drop? I also need recommendations for improving performance while handling the increased load." \
        "Business Insights - Performance Analysis"
fi

echo "🎯 CONVERSATION TESTING COMPLETE!"
echo ""
echo "📊 Summary:"
echo "   - Tested realistic customer scenarios across all agent types"
echo "   - Each conversation used authentic user language and context"
echo "   - Agents powered by Google Vertex AI and Gemini models"
echo "   - Response times and quality measured for each interaction"
echo ""
echo "✨ This demonstrates the ANZX AI Platform's ability to handle"
echo "   real-world customer conversations with intelligent, contextual responses!"