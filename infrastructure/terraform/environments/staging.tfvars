# Staging environment configuration
project_id = "anzx-ai-staging"
region     = "australia-southeast1"
zone       = "australia-southeast1-a"
environment = "staging"

# Domain configuration
domain_name = "staging.anzx.ai"

# Database configuration
database_tier = "db-custom-2-4096"  # Medium instance for staging

# Scaling configuration
min_instances = 1
max_instances = 8

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