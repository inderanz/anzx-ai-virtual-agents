#!/bin/bash

# This script automates the setup of Firebase Authentication for the ANZx.ai project.

set -e
set -x # Enable debugging

PROJECT_ID="extreme-gecko-466211-t1"
WEB_APP_NICKNAME="auth-frontend-anzx-ai"
CONFIG_FILE="services/auth-frontend/src/firebase-config.js"

echo "ðŸ”¥ Automating Firebase Setup for project: $PROJECT_ID..."

# Check for required tools
if ! command -v gcloud &> /dev/null || ! command -v firebase &> /dev/null; then
    echo "â Error: 'gcloud' and 'firebase' CLI tools are required. Please install them."
    exit 1
fi

echo "
ðŸ”‘ Step 1: Enabling required Google Cloud services..."
gcloud services enable firebase.googleapis.com \
    identitytoolkit.googleapis.com \
    --project=$PROJECT_ID
echo "âœ… Services enabled."


echo "
ðŸ›  Step 2: Checking for existing Firebase web app..."
APP_ID=$(firebase apps:list --project $PROJECT_ID | grep 'auth-frontend-anzx-ai' | awk -F '│' '{print $3}' | tr -d ' ' || true)

if [ -z "$APP_ID" ]; then
    echo "ðŸš€ No existing web app found. Creating a new one..."
    # Capture output and parse App ID
    CREATE_OUTPUT=$(firebase apps:create WEB "$WEB_APP_NICKNAME" --project $PROJECT_ID)
    echo "Create output: $CREATE_OUTPUT"
    APP_ID=$(echo "$CREATE_OUTPUT" | grep "App ID" | awk '{print $4}')
    echo "âœ… Web app created with nickname: $WEB_APP_NICKNAME and App ID: $APP_ID"
else
    echo "âœ… Found existing web app with nickname: $WEB_APP_NICKNAME and App ID: $APP_ID"
fi

if [ -z "$APP_ID" ]; then
    echo "â Error: Could not determine Firebase App ID after create/check."
    exit 1
fi

echo "
ðŸ’¡ ACTION REQUIRED: Please run the following command to get your Firebase config:"
echo "---------------------------------------------------------------------"
echo "firebase apps:sdkconfig WEB '$APP_ID' --project $PROJECT_ID"
echo "---------------------------------------------------------------------"
echo "
Then, copy the JSON output and paste it into this file: $CONFIG_FILE"

echo "
ðŸŽ‰ Firebase setup is complete after you update the config file!"
