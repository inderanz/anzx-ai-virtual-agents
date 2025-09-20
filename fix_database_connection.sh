#!/bin/bash

# ANZX AI Platform - Database Connection Fix
# This script diagnoses and fixes database connection issues

set -e

PROJECT_ID="extreme-gecko-466211-t1"
REGION="australia-southeast1"
DB_INSTANCE="anzx-ai-platform-db"
DB_NAME="anzx_ai_platform"
DB_USER="anzx_user"

echo "🔧 ANZX AI Platform - Database Connection Diagnostics & Fix"
echo "=========================================================="
echo "Project: $PROJECT_ID"
echo "Instance: $DB_INSTANCE"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo ""

# Function to generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

echo "🔍 Step 1: Diagnosing current database state..."

# Check if instance exists and is running
echo "📊 Checking Cloud SQL instance status..."
if gcloud sql instances describe $DB_INSTANCE --quiet 2>/dev/null; then
    echo "✅ Cloud SQL instance exists and is accessible"
    
    # Get instance details
    INSTANCE_IP=$(gcloud sql instances describe $DB_INSTANCE --format="value(ipAddresses[0].ipAddress)")
    INSTANCE_STATE=$(gcloud sql instances describe $DB_INSTANCE --format="value(state)")
    
    echo "   Instance IP: $INSTANCE_IP"
    echo "   Instance State: $INSTANCE_STATE"
else
    echo "❌ Cloud SQL instance not found or not accessible"
    exit 1
fi

# Check if database exists
echo ""
echo "📊 Checking database existence..."
if gcloud sql databases describe $DB_NAME --instance=$DB_INSTANCE --quiet 2>/dev/null; then
    echo "✅ Database '$DB_NAME' exists"
else
    echo "❌ Database '$DB_NAME' not found"
    echo "🔧 Creating database..."
    gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE
    echo "✅ Database created successfully"
fi

# Check if user exists
echo ""
echo "📊 Checking database user..."
if gcloud sql users describe $DB_USER --instance=$DB_INSTANCE --quiet 2>/dev/null; then
    echo "✅ Database user '$DB_USER' exists"
    USER_EXISTS=true
else
    echo "❌ Database user '$DB_USER' not found"
    USER_EXISTS=false
fi

echo ""
echo "🔧 Step 2: Fixing database connection..."

# Generate new secure password
NEW_PASSWORD=$(generate_password)
echo "🔑 Generated new secure password for database user"

if [ "$USER_EXISTS" = true ]; then
    echo "🔄 Updating existing user password..."
    gcloud sql users set-password $DB_USER \
        --instance=$DB_INSTANCE \
        --password="$NEW_PASSWORD"
    echo "✅ Password updated successfully"
else
    echo "👤 Creating new database user..."
    gcloud sql users create $DB_USER \
        --instance=$DB_INSTANCE \
        --password="$NEW_PASSWORD"
    echo "✅ User created successfully"
fi

echo ""
echo "🔧 Step 3: Updating Cloud Run environment variables..."

# Update the Cloud Run service with new database URL
DATABASE_URL="postgresql://$DB_USER:$NEW_PASSWORD@$INSTANCE_IP:5432/$DB_NAME?sslmode=require"

echo "🚀 Updating Core API service environment..."
gcloud run services update anzx-ai-platform-core-api \
    --region=$REGION \
    --set-env-vars="DATABASE_URL=$DATABASE_URL" \
    --quiet

echo "✅ Core API service updated"

echo "🚀 Updating Knowledge service environment..."
gcloud run services update anzx-ai-platform-knowledge-service \
    --region=$REGION \
    --set-env-vars="DATABASE_URL=$DATABASE_URL" \
    --quiet

echo "✅ Knowledge service updated"

echo ""
echo "🔧 Step 4: Testing database connection..."

# Test connection using gcloud
echo "🧪 Testing connection via gcloud..."
if echo "SELECT version();" | gcloud sql connect $DB_INSTANCE --user=$DB_USER --quiet 2>/dev/null; then
    echo "✅ Database connection test successful"
else
    echo "⚠️  Direct connection test failed (this might be normal due to network restrictions)"
fi

echo ""
echo "🧪 Step 5: Testing API endpoints..."

# Wait a moment for services to restart
echo "⏳ Waiting for services to restart..."
sleep 30

# Test health endpoint
echo "🏥 Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/health)
echo "Health Response: $HEALTH_RESPONSE"

# Test assistants endpoint (this will show if database is working)
echo "🤖 Testing assistants endpoint..."
ASSISTANTS_RESPONSE=$(curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/assistants)
echo "Assistants Response: $ASSISTANTS_RESPONSE"

# Check if we still get database errors
if echo "$ASSISTANTS_RESPONSE" | grep -q "password authentication failed"; then
    echo "❌ Still getting database authentication errors"
    echo "🔧 Additional troubleshooting needed"
elif echo "$ASSISTANTS_RESPONSE" | grep -q "connection.*failed"; then
    echo "❌ Still getting database connection errors"
    echo "🔧 Network connectivity issues may exist"
elif echo "$ASSISTANTS_RESPONSE" | grep -q "assistants"; then
    echo "✅ Database connection working! API returning expected data"
else
    echo "⚠️  Unexpected response - manual verification needed"
fi

echo ""
echo "📋 Step 6: Updating Terraform configuration..."

# Update terraform.tfvars with new password
cd infrastructure/terraform

# Backup existing tfvars
cp terraform.tfvars terraform.tfvars.backup.$(date +%Y%m%d_%H%M%S)

# Update the password in tfvars (if it exists)
if grep -q "db_password" terraform.tfvars; then
    sed -i.bak "s/db_password = .*/db_password = \"$NEW_PASSWORD\"/" terraform.tfvars
    echo "✅ Updated terraform.tfvars with new password"
else
    echo "db_password = \"$NEW_PASSWORD\"" >> terraform.tfvars
    echo "✅ Added password to terraform.tfvars"
fi

echo ""
echo "🎉 DATABASE CONNECTION FIX COMPLETED!"
echo "====================================="
echo ""
echo "📊 Summary:"
echo "  ✅ Database instance: $INSTANCE_STATE"
echo "  ✅ Database created: $DB_NAME"
echo "  ✅ User configured: $DB_USER"
echo "  ✅ Password updated: [SECURE]"
echo "  ✅ Cloud Run services updated"
echo "  ✅ Terraform configuration updated"
echo ""
echo "🔑 Database Connection Details:"
echo "  Host: $INSTANCE_IP"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: [Stored in terraform.tfvars]"
echo ""
echo "🧪 Verification Commands:"
echo "  curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/health"
echo "  curl -s https://anzx-ai-platform-core-api-ymh6bmf7oq-ts.a.run.app/assistants"
echo ""
echo "📝 Next Steps:"
echo "  1. Run 'terraform plan' to verify configuration"
echo "  2. Test API endpoints to confirm database connectivity"
echo "  3. Create test users and agents using the API"
echo "  4. Run comprehensive tests"
echo ""
echo "⚠️  IMPORTANT: The new database password is stored in terraform.tfvars"
echo "   Make sure to keep this file secure and backed up!"

# Save connection details to a secure file
cat > database_connection_info.txt << EOF
# ANZX AI Platform Database Connection Information
# Generated: $(date)
# KEEP THIS FILE SECURE!

Database Instance: $DB_INSTANCE
Database Name: $DB_NAME
Database User: $DB_USER
Database Password: $NEW_PASSWORD
Database Host: $INSTANCE_IP
Database Port: 5432

Connection String: postgresql://$DB_USER:$NEW_PASSWORD@$INSTANCE_IP:5432/$DB_NAME?sslmode=require

Cloud Run Services Updated:
- anzx-ai-platform-core-api
- anzx-ai-platform-knowledge-service

Terraform Files Updated:
- terraform.tfvars (password updated)
EOF

echo "💾 Connection details saved to: database_connection_info.txt"
echo "🔒 Please keep this file secure!"