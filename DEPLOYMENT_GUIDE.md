# ANZX AI Platform - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the ANZX AI Platform to Google Cloud Platform using the project `extreme-gecko-466211-t1`.

## Prerequisites

- Google Cloud SDK installed and authenticated
- Docker installed
- Node.js 18+ installed
- Python 3.11+ installed
- Access to the `extreme-gecko-466211-t1` project

## Quick Start Deployment

For a complete automated deployment, run:

```bash
# 1. Set up secrets and database
./scripts/setup-production-secrets.sh
./scripts/setup-database.sh

# 2. Deploy to Cloud Run
./scripts/deploy-to-cloudrun.sh

# 3. Set up backup and disaster recovery
./scripts/setup-backup-disaster-recovery.sh

# 4. Launch beta program
./scripts/setup-beta-program.sh
```

## Detailed Deployment Steps

### 1. Environment Setup

#### 1.1 Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project extreme-gecko-466211-t1
```

#### 1.2 Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable sql.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
```

### 2. Infrastructure Setup

#### 2.1 Create Artifact Registry

```bash
gcloud artifacts repositories create anzx-ai-platform-docker \
    --repository-format=docker \
    --location=australia-southeast1 \
    --description="Docker repository for ANZX AI Platform"
```

#### 2.2 Configure Docker Authentication

```bash
gcloud auth configure-docker australia-southeast1-docker.pkg.dev
```

### 3. Database Setup

#### 3.1 Create Cloud SQL Instance

```bash
# Run the database setup script
./scripts/setup-database.sh
```

This will create:
- PostgreSQL 15 instance with pgvector extension
- Private IP configuration
- Automated backups
- Point-in-time recovery

#### 3.2 Verify Database Connection

```bash
gcloud sql connect anzx-ai-platform-db --user=anzx_user --database=anzx_ai_platform
```

### 4. Secrets Management

#### 4.1 Create Production Secrets

```bash
# Run the secrets setup script
./scripts/setup-production-secrets.sh
```

#### 4.2 Update Secret Values

Update the following secrets with real values:

```bash
# Stripe keys
echo -n "sk_live_your_stripe_secret_key" | gcloud secrets versions add anzx-ai-platform-stripe-secret --data-file=-

# OpenAI API key (if using)
echo -n "sk-your_openai_key" | gcloud secrets versions add anzx-ai-platform-openai-key --data-file=-

# Update database URL with real IP
DB_IP=$(gcloud sql instances describe anzx-ai-platform-db --format="value(ipAddresses[0].ipAddress)")
echo -n "postgresql://anzx_user:your_password@$DB_IP:5432/anzx_ai_platform" | gcloud secrets versions add anzx-ai-platform-db-url --data-file=-
```

### 5. Application Deployment

#### 5.1 Build and Deploy Services

```bash
# Run the deployment script
./scripts/deploy-to-cloudrun.sh
```

This will:
- Build Docker images for all services
- Push images to Artifact Registry
- Deploy to Cloud Run with proper configuration
- Set up VPC connector for private database access

#### 5.2 Verify Deployment

```bash
# Check service status
gcloud run services list --region=australia-southeast1

# Test API health
API_URL=$(gcloud run services describe anzx-ai-core-api --region=australia-southeast1 --format="value(status.url)")
curl "$API_URL/health"
```

### 6. Monitoring and Alerting

#### 6.1 Set Up Monitoring

```bash
# Create notification channel
gcloud alpha monitoring channels create \
    --display-name="Production Alerts" \
    --type="email" \
    --channel-labels="email_address=alerts@anzx-ai.com"
```

#### 6.2 Configure Alerts

The deployment script automatically creates alerts for:
- High error rates
- Service downtime
- Database connection issues
- Memory/CPU usage

### 7. Backup and Disaster Recovery

#### 7.1 Set Up Backup System

```bash
# Run the backup setup script
./scripts/setup-backup-disaster-recovery.sh
```

This configures:
- Daily automated database backups
- Cross-region backup replication
- Disaster recovery procedures
- Data export compliance functions

#### 7.2 Test Backup Restoration

```bash
# List available backups
gcloud sql backups list --instance=anzx-ai-platform-db

# Test restore (to a test instance)
gcloud sql instances create test-restore-instance \
    --database-version=POSTGRES_15 \
    --tier=db-custom-1-4096 \
    --region=australia-southeast1

gcloud sql backups restore BACKUP_ID \
    --restore-instance=test-restore-instance
```

### 8. Beta Program Launch

#### 8.1 Set Up Beta Environment

```bash
# Run the beta program setup script
./scripts/setup-beta-program.sh
```

This creates:
- Staging environment
- Beta user signup system
- Feedback collection system
- Beta program dashboard

#### 8.2 Configure Beta Landing Page

Update the beta landing page at `website/beta/index.html` with:
- Your actual function URLs
- Company-specific messaging
- Contact information

### 9. Domain and SSL Configuration

#### 9.1 Configure Custom Domain

```bash
# Map custom domain to Cloud Run service
gcloud run domain-mappings create \
    --service=anzx-ai-core-api \
    --domain=api.anzx-ai.com \
    --region=australia-southeast1
```

#### 9.2 Set Up Load Balancer (Optional)

For advanced routing and CDN:

```bash
# Create global load balancer
gcloud compute backend-services create anzx-ai-backend \
    --global \
    --protocol=HTTP

# Add Cloud Run as backend
gcloud compute backend-services add-backend anzx-ai-backend \
    --global \
    --network-endpoint-group=anzx-ai-neg \
    --network-endpoint-group-region=australia-southeast1
```

### 10. CI/CD Pipeline

#### 10.1 Set Up Cloud Build Trigger

```bash
# Create build trigger for main branch
gcloud builds triggers create github \
    --repo-name=anzx-ai-platform \
    --repo-owner=your-github-username \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --name=anzx-ai-platform-deploy
```

#### 10.2 Configure Branch Protection

In your GitHub repository:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Require status checks to pass
4. Require pull request reviews

## Post-Deployment Checklist

### Security Checklist

- [ ] All secrets are stored in Secret Manager
- [ ] Database uses private IP only
- [ ] VPC connector configured for service communication
- [ ] SSL/TLS enabled for all endpoints
- [ ] IAM roles follow principle of least privilege
- [ ] Audit logging enabled

### Performance Checklist

- [ ] Auto-scaling configured appropriately
- [ ] Database connection pooling enabled
- [ ] CDN configured for static assets
- [ ] Monitoring and alerting active
- [ ] Load testing completed

### Compliance Checklist

- [ ] Data stored in Australian regions only
- [ ] Privacy policy updated and accessible
- [ ] Data export functionality tested
- [ ] Backup and recovery procedures documented
- [ ] Incident response plan in place

## Monitoring and Maintenance

### Daily Checks

- Review error logs and alerts
- Check service health endpoints
- Monitor resource usage
- Verify backup completion

### Weekly Checks

- Review performance metrics
- Check security alerts
- Update dependencies if needed
- Test disaster recovery procedures

### Monthly Checks

- Review and rotate secrets
- Update documentation
- Conduct security review
- Plan capacity scaling

## Troubleshooting

### Common Issues

#### Service Won't Start

```bash
# Check logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=anzx-ai-core-api" --limit=50

# Check environment variables
gcloud run services describe anzx-ai-core-api --region=australia-southeast1
```

#### Database Connection Issues

```bash
# Test database connectivity
gcloud sql connect anzx-ai-platform-db --user=anzx_user

# Check VPC connector
gcloud compute networks vpc-access connectors describe anzx-ai-platform-connector --region=australia-southeast1
```

#### High Error Rates

```bash
# Check application logs
gcloud logs read "resource.type=cloud_run_revision" --filter="severity>=ERROR" --limit=100

# Check resource usage
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"
```

## Support and Resources

### Documentation
- [API Documentation](https://api.anzx-ai.com/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL Documentation](https://cloud.google.com/sql/docs)

### Support Channels
- Email: support@anzx-ai.com
- Emergency: alerts@anzx-ai.com
- Status Page: https://status.anzx-ai.com

### Useful Commands

```bash
# View all services
gcloud run services list --region=australia-southeast1

# Scale service
gcloud run services update anzx-ai-core-api \
    --region=australia-southeast1 \
    --min-instances=2 \
    --max-instances=50

# View logs
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=anzx-ai-core-api"

# Update service with new image
gcloud run deploy anzx-ai-core-api \
    --image=australia-southeast1-docker.pkg.dev/extreme-gecko-466211-t1/anzx-ai-platform-docker/core-api:latest \
    --region=australia-southeast1
```

## Cost Optimization

### Resource Right-Sizing

- Monitor CPU and memory usage
- Adjust instance sizes based on actual usage
- Use preemptible instances for non-critical workloads

### Storage Optimization

- Implement lifecycle policies for backups
- Use appropriate storage classes
- Regular cleanup of unused resources

### Network Optimization

- Use VPC peering for internal communication
- Implement CDN for static content
- Optimize database queries to reduce network traffic

---

**Deployment Complete!** 🎉

Your ANZX AI Platform is now running in production on Google Cloud Platform. Monitor the health dashboards and be ready to scale based on user demand.

For any issues or questions, refer to the troubleshooting section or contact the support team.