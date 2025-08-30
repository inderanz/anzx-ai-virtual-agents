# Development environment configuration
project_id = "anzx-ai-dev"
region     = "australia-southeast1"
zone       = "australia-southeast1-a"
environment = "dev"

# Domain configuration
domain_name = "dev.anzx.ai"

# Database configuration
database_tier = "db-custom-1-3840"  # Smaller instance for dev

# Scaling configuration
min_instances = 0  # Scale to zero in dev
max_instances = 5

# Enable development APIs
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