#!/bin/bash

# ANZx.ai Platform Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Example: ./deploy.sh dev plan
# Example: ./deploy.sh prod apply

set -e

ENVIRONMENT=${1:-dev}
ACTION=${2:-plan}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$SCRIPT_DIR/../terraform"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo "Error: Environment must be dev, staging, or prod"
    exit 1
fi

# Validate action
if [[ ! "$ACTION" =~ ^(plan|apply|destroy|init|validate)$ ]]; then
    echo "Error: Action must be plan, apply, destroy, init, or validate"
    exit 1
fi

echo "🚀 ANZx.ai Platform Deployment"
echo "Environment: $ENVIRONMENT"
echo "Action: $ACTION"
echo "================================"

# Change to terraform directory
cd "$TERRAFORM_DIR"

# Initialize Terraform if needed
if [ "$ACTION" = "init" ] || [ ! -d ".terraform" ]; then
    echo "📦 Initializing Terraform..."
    terraform init \
        -backend-config="bucket=anzx-terraform-state-$ENVIRONMENT" \
        -backend-config="prefix=platform/$ENVIRONMENT"
fi

# Validate Terraform configuration
if [ "$ACTION" = "validate" ] || [ "$ACTION" = "plan" ] || [ "$ACTION" = "apply" ]; then
    echo "✅ Validating Terraform configuration..."
    terraform validate
fi

# Select workspace
echo "🔧 Selecting workspace: $ENVIRONMENT"
terraform workspace select "$ENVIRONMENT" || terraform workspace new "$ENVIRONMENT"

# Execute the requested action
case $ACTION in
    plan)
        echo "📋 Planning infrastructure changes..."
        terraform plan \
            -var-file="environments/$ENVIRONMENT.tfvars" \
            -out="$ENVIRONMENT.tfplan"
        ;;
    apply)
        echo "🏗️  Applying infrastructure changes..."
        if [ -f "$ENVIRONMENT.tfplan" ]; then
            terraform apply "$ENVIRONMENT.tfplan"
        else
            terraform apply \
                -var-file="environments/$ENVIRONMENT.tfvars" \
                -auto-approve
        fi
        
        # Clean up plan file
        rm -f "$ENVIRONMENT.tfplan"
        
        echo "✅ Deployment completed successfully!"
        echo ""
        echo "📊 Infrastructure outputs:"
        terraform output
        ;;
    destroy)
        echo "⚠️  WARNING: This will destroy all infrastructure in $ENVIRONMENT!"
        read -p "Are you sure? Type 'yes' to continue: " -r
        if [[ $REPLY = "yes" ]]; then
            terraform destroy \
                -var-file="environments/$ENVIRONMENT.tfvars" \
                -auto-approve
            echo "💥 Infrastructure destroyed!"
        else
            echo "❌ Destroy cancelled"
        fi
        ;;
    init)
        echo "✅ Terraform initialized successfully!"
        ;;
    validate)
        echo "✅ Terraform configuration is valid!"
        ;;
esac

echo ""
echo "🎉 Operation completed: $ACTION for $ENVIRONMENT"