#!/bin/bash

# ANZX AI Platform - Customer Setup & Test Script

set -e

BASE_URL="https://anzx-ai-platform-core-api-1088103632448.australia-southeast1.run.app"

if [ -z "$AUTH_TOKEN" ]; then
    echo "â AUTH_TOKEN environment variable is not set."
    echo "Please provide a valid JWT token to run this script."
    exit 1
fi

AUTH_HEADER="Authorization: Bearer $AUTH_TOKEN"

echo "ðŸ€‘ Simulating Enterprise Customer Setup for 'Acme Corporation'"

echo "
â Step 1: Retrieving Test Organization ID..."
# The test user should belong to an organization. We get the ID from the /me endpoint.
ORG_ID=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/api/v1/auth/me" | jq -r '.organization_id')

if [ -z "$ORG_ID" ] || [ "$ORG_ID" == "null" ]; then
    echo "â Failed to retrieve Organization ID. Is the user part of an organization?"
    exit 1
fi
echo "ðŸ… Found Organization ID: $ORG_ID"

echo "
ðŸ Step 2: Uploading 'acme_corp_policy.md' to the Knowledge Base..."
UPLOAD_RESPONSE=$(curl -s -X POST \
  -H "$AUTH_HEADER" \
  -F "file=@acme_corp_policy.md" \
  -F "name=Acme Corp Employee Handbook" \
  "$BASE_URL/api/knowledge/sources/upload")

KNOWLEDGE_SOURCE_ID=$(echo $UPLOAD_RESPONSE | jq -r '.id') # Adjusted to get id from the root

if [ -z "$KNOWLEDGE_SOURCE_ID" ] || [ "$KNOWLEDGE_SOURCE_ID" == "null" ]; then
    echo "â Failed to upload knowledge document. Response:"
    echo $UPLOAD_RESPONSE
    exit 1
fi
echo "ðŸ… Knowledge Source created with ID: $KNOWLEDGE_SOURCE_ID"

echo "
ðŸ Step 3: Retrieving the 'Test Support Agent' ID..."
# Use the authenticated endpoint to get agents for the organization
SUPPORT_AGENT_ID=$(curl -s -H "$AUTH_HEADER" "$BASE_URL/api/v1/agents/" | jq -r '.[] | select(.name=="Test Support Agent") | .id')

if [ -z "$SUPPORT_AGENT_ID" ] || [ "$SUPPORT_AGENT_ID" == "null" ]; then
    echo "â Failed to retrieve Support Agent ID. Exiting."
    exit 1
fi
echo "ðŸ… Found Support Agent ID: $SUPPORT_AGENT_ID"

echo "
ðŸ’¬ Step 4: Asking the agent a question about the uploaded data..."
USER_QUESTION="How many vacation days do I get per year?"
echo "  ðŸ‘¤ User Question: '$USER_QUESTION'"

CHAT_PAYLOAD=$(jq -n \
  --arg message "$USER_QUESTION" \
  '{message: $message, channel: "customer-test"}')

CHAT_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "$CHAT_PAYLOAD" \
  "$BASE_URL/api/v1/agents/$SUPPORT_AGENT_ID/chat")

AI_REPLY=$(echo $CHAT_RESPONSE | jq -r '.reply')

if [ -z "$AI_REPLY" ] || [ "$AI_REPLY" == "null" ]; then
    echo "â Did not receive a reply from the AI. Response:"
    echo $CHAT_RESPONSE
    exit 1
fi

echo "
ðŸ¤– AI Response:"
echo "  $AI_REPLY"

echo "
ðŸŽ‰ Verification Complete!"
echo "The script successfully uploaded a custom document and asked a question about its content."
