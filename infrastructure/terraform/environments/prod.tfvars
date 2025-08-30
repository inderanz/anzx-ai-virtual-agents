# Production environment configuration
project_id = "anzx-ai-prod"
region     = "australia-southeast1"
zone       = "australia-southeast1-a"
environment = "prod"

# Domain configuration
domain_name = "anzx.ai"

# Database configuration
database_tier = "db-custom-4-8192"  # Large instance for production

# Scaling configuration
min_instances = 2  # Always keep instances warm
max_instances = 20

# Enable all APIs
enable_apis = [
  "run.googleapis.com",
  "sql-component.googleapis.com",
  "sqladmin.googleapis.com",
  "cloudbuild.googleapis.com",
  "containerregistry.googleapis.com",
  "artifactregistry.googleapis.com",
  "cloudkms.googleapis.com",
  "secretmanager.googleapis.com",
  "monitoring.googleapis.com",
  "logging.googleapis.com",
  "cloudtrace.googleapis.com",
  "clouderrorreporting.googleapis.com",
  "aiplatform.googleapis.com",
  "documentai.googleapis.com",
  "storage.googleapis.com",
  "redis.googleapis.com",
  "vpcaccess.googleapis.com"
]