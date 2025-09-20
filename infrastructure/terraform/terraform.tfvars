# ANZX AI Platform - Production Configuration
project_id = "extreme-gecko-466211-t1"
region     = "australia-southeast1"
zone       = "australia-southeast1-a"

# Domain and GitHub configuration
domain_name  = "anzx.ai"
github_owner = "anzx-ai"
github_repo  = "anzx-ai-virtual-agents"
alert_email  = "admin@anzx.ai"

# Database configuration (Free tier optimized)
db_name     = "anzx_ai_platform"
db_user     = "anzx_user"
db_password = "szsQFdVWtTIU4aL3jq8DR8tg6"
db_tier     = "db-f1-micro"  # Free tier: 0.6GB RAM, shared CPU

# Redis configuration (Free tier optimized)
redis_memory_size = 1  # Minimum 1GB for Redis

# GKE configuration (Free tier optimized)
gke_num_nodes    = 1  # Start with 1 node for free tier
gke_min_nodes    = 1
gke_max_nodes    = 3  # Limit max nodes for cost control
gke_machine_type = "e2-micro"  # Free tier eligible

# Security configuration
jwt_secret_key    = "anzx-ai-jwt-secret-key-2024-production"
stripe_secret_key = "sk_test_placeholder_for_production"
vertex_ai_project = "extreme-gecko-466211-t1"

# Scaling configuration (Free tier optimized)
api_min_instances = 0  # Allow scaling to 0 to save costs
api_max_instances = 10  # Limit max instances for cost control
api_cpu_limit     = "1000m"  # 1 vCPU limit for free tier
api_memory_limit  = "2Gi"   # 2GB memory limit for free tier

# Feature flags
enable_blue_green_deployment = true
enable_auto_scaling         = true
enable_ssl                  = true
enable_monitoring           = true
enable_backup              = true

# Compliance
enable_audit_logs           = true
data_location_restriction   = "australia-southeast1"
enable_encryption_at_rest   = true
enable_private_cluster      = true