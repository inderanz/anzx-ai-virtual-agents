#!/bin/bash
# Database connection script for testing
echo "🔌 Starting Cloud SQL Auth Proxy..."
./cloud_sql_proxy -instances=extreme-gecko-466211-t1:australia-southeast1:anzx-ai-platform-db=tcp:5432 &
PROXY_PID=$!
echo "Cloud SQL Auth Proxy started with PID: $PROXY_PID"
echo "Database available at: localhost:5432"
echo "To stop proxy: kill $PROXY_PID"
echo "Connection string: postgresql://anzx_user:AnzxAI2024!SecureDB@localhost:5432/anzx_ai_platform"
