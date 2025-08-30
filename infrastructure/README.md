# ANZx.ai Platform Infrastructure

This directory contains the Infrastructure as Code (IaC) configuration for the ANZx.ai platform using Terraform and Google Cloud Platform.

## Architecture Overview

The platform is deployed on Google Cloud Platform with the following components:

- **Cloud Run** - Containerized microservices (Core API, Agent Orchestration, Knowledge Service)
- **Cloud SQL** - PostgreSQL with pgvector extension for embeddings
- **Memorystore Redis** - Caching and message queuing
- **Cloud Storage** - Document storage and static assets
- **Artifact Registry** - Container image registry
- **Cloud Build** - CI/CD pipelines
- **Cloud KMS** - Encryption key management
- **Secret Manager** - Secure secret storage
- **Cloud Monitoring** - Observability and alerting

## Prerequisites

1. **Google Cloud SDK** installed and configured
2. **Terraform** >= 1.0 installed
3. **GCP Organization** with billing enabled
4. **GitHub repository** connected to Cloud Build

## Initial Setup

### 1. GCP Project Setup

Run the setup script to create GCP projects and prerequisites:

```bash
# Get your organization and billing account IDs
gcloud organizations list
gcloud billing accounts list

# Run setup script
./scripts/setup-gcp.sh [ORGANIZATION_ID] [BILLING_ACCOUNT_ID]
```

This script will:
- Create dev, staging, and prod GCP projects
- Enable required APIs
- Create Terraform state buckets
- Set up service accounts and permissions

### 2. Configure Authentication

```bash
# Set the service account key for Terraform
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/terraform-key.json

# Verify authentication
gcloud auth list
```

### 3. Update Configuration

Update the following files with your actual values:

1. **Project IDs** in `terraform/cloudbuild.tf`
2. **GitHub repository** details in Cloud Build triggers
3. **Domain names** in environment `.tfvars` files
4. **Slack webhook URLs** in monitoring configuration

## Deployment

### Development Environment

```bash
# Initialize Terraform
./scripts/deploy.sh dev init

# Plan infrastructure changes
./scripts/deploy.sh dev plan

# Apply changes
./scripts/deploy.sh dev apply
```

### Staging Environment

```bash
./scripts/deploy.sh staging plan
./scripts/deploy.sh staging apply
```

### Production Environment

```bash
./scripts/deploy.sh prod plan
./scripts/deploy.sh prod apply
```

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── main.tf              # Main Terraform configuration
│   ├── variables.tf         # Input variables
│   ├── outputs.tf           # Output values
│   ├── apis.tf             # GCP API enablement
│   ├── networking.tf       # VPC and networking
│   ├── database.tf         # Cloud SQL configuration
│   ├── redis.tf            # Memorystore Redis
│   ├── storage.tf          # Cloud Storage buckets
│   ├── security.tf         # KMS, secrets, IAM
│   ├── cloud_run.tf        # Cloud Run services
│   ├── monitoring.tf       # Monitoring and alerting
│   ├── cloudbuild.tf       # CI/CD configuration
│   └── environments/       # Environment-specific configs
│       ├── dev.tfvars
│       ├── staging.tfvars
│       └── prod.tfvars
├── cloudbuild/             # Cloud Build pipeline configs
│   ├── core-api.yaml
│   ├── agent-orchestration.yaml
│   ├── knowledge-service.yaml
│   └── chat-widget.yaml
└── scripts/                # Deployment scripts
    ├── deploy.sh           # Main deployment script
    └── setup-gcp.sh        # Initial GCP setup
```

## Environment Configuration

### Development
- **Project**: `anzx-ai-dev`
- **Domain**: `dev.anzx.ai`
- **Scaling**: 0-5 instances (scale to zero)
- **Database**: Small instance, single zone
- **Redis**: Basic tier

### Staging
- **Project**: `anzx-ai-staging`
- **Domain**: `staging.anzx.ai`
- **Scaling**: 1-8 instances
- **Database**: Medium instance, single zone
- **Redis**: Standard tier

### Production
- **Project**: `anzx-ai-prod`
- **Domain**: `anzx.ai`
- **Scaling**: 2-20 instances (always warm)
- **Database**: Large instance, regional HA with read replica
- **Redis**: Standard HA tier

## Security Features

- **Encryption at rest** using Cloud KMS
- **Private networking** with VPC and private service access
- **Secret management** with Secret Manager
- **IAM roles** with least privilege access
- **Container scanning** in CI/CD pipelines
- **TLS 1.2+** for all external communications

## Monitoring and Alerting

The infrastructure includes comprehensive monitoring:

- **SLOs** for availability and latency
- **Alert policies** for error rates, latency, and resource usage
- **Custom dashboard** with key metrics
- **Notification channels** for email and Slack

## CI/CD Pipeline

Each service has automated CI/CD with:

1. **Build** - Docker image creation
2. **Test** - Unit and integration tests
3. **Security scan** - Container vulnerability scanning
4. **Deploy** - Automated deployment to Cloud Run
5. **Health check** - Post-deployment verification

## Disaster Recovery

- **Automated backups** with point-in-time recovery
- **Cross-region replication** for production
- **Infrastructure as Code** for rapid environment recreation
- **Monitoring and alerting** for proactive issue detection

## Cost Optimization

- **Auto-scaling** based on demand
- **Scale-to-zero** for development environments
- **Lifecycle policies** for storage buckets
- **Resource right-sizing** per environment

## Troubleshooting

### Common Issues

1. **Permission denied errors**
   ```bash
   # Verify service account permissions
   gcloud auth list
   gcloud projects get-iam-policy [PROJECT_ID]
   ```

2. **Terraform state issues**
   ```bash
   # List workspaces
   terraform workspace list
   
   # Switch workspace
   terraform workspace select [ENVIRONMENT]
   ```

3. **API not enabled errors**
   ```bash
   # Enable required APIs manually
   gcloud services enable [API_NAME] --project=[PROJECT_ID]
   ```

### Useful Commands

```bash
# View infrastructure outputs
terraform output

# Check service status
gcloud run services list --project=[PROJECT_ID]

# View logs
gcloud logging read "resource.type=cloud_run_revision" --project=[PROJECT_ID]

# Check database status
gcloud sql instances list --project=[PROJECT_ID]
```

## Support

For infrastructure issues:
1. Check the monitoring dashboard
2. Review Cloud Build logs
3. Examine Terraform state and outputs
4. Contact the platform team with specific error messages