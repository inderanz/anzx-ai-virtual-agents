# ANZX AI Platform - Production Configuration
# Project: extreme-gecko-466211-t1

project_id = "extreme-gecko-466211-t1"
region     = "australia-southeast1"
zone       = "australia-southeast1-a"

# Domain configuration
domain_name = "anzx-ai.com"

# GitHub configuration
github_owner = "your-github-username"
github_repo  = "anzx-ai-platform"

# Alert configuration
alert_email = "alerts@anzx-ai.com"

# Database configuration
db_name     = "anzx_ai_platform"
db_user     = "anzx_user"
db_password = "your-secure-db-password-here"
db_tier     = "db-custom-2-8192"
db_disk_size = 100

# Redis configuration
redis_memory_size = 4

# GKE configuration (for future blue-green deployments)
gke_num_nodes    = 3
gke_min_nodes    = 1
gke_max_nodes    = 10
gke_machine_type = "e2-standard-4"

# Security configuration
jwt_secret_key    = "your-jwt-secret-key-here"
stripe_secret_key = "your-stripe-secret-key-here"
openai_api_key    = "your-openai-api-key-here"
vertex_ai_project = "extreme-gecko-466211-t1"

# Environment configuration
environment = "production"

# Feature flags
enable_monitoring           = true
enable_backup              = true
backup_retention_days      = 30
enable_blue_green_deployment = true
enable_auto_scaling        = true
enable_ssl                 = true
enable_cdn                 = true

# Scaling configuration
api_min_instances = 2
api_max_instances = 100
api_cpu_limit     = "2000m"
api_memory_limit  = "4Gi"

# Compliance configuration
enable_audit_logs           = true
data_location_restriction   = "australia-southeast1"
enable_encryption_at_rest   = true
enable_private_cluster      = true