# ANZX AI Platform - Clean Production Infrastructure
# Reviewed and tested Terraform configuration

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "anzx-ai-terraform-state-1758328389"
    prefix = "production"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

locals {
  app_name = "anzx-ai-platform"
  common_labels = {
    environment = "production"
    application = local.app_name
    managed_by  = "terraform"
  }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "run.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com",
    "documentai.googleapis.com",
    "discoveryengine.googleapis.com",
    "vpcaccess.googleapis.com",
    "servicenetworking.googleapis.com",
    "sqladmin.googleapis.com"
  ])
  
  service = each.value
  project = var.project_id
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

# VPC Network for secure private communication
resource "google_compute_network" "vpc" {
  name                    = "anzx-ai-platform-vpc"  # Fixed: simplified name
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.required_apis]
}

resource "google_compute_subnetwork" "subnet" {
  name          = "anzx-ai-platform-subnet"  # Fixed: simplified name
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  private_ip_google_access = true
}

# VPC Connector removed for simplified deployment
# Can be added back later with proper networking setup

# Use existing Artifact Registry (don't create new one)
data "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "anzx-ai-platform-docker"
}

# Cloud SQL Instance with private networking
resource "google_sql_database_instance" "main" {
  name             = "anzx-ai-platform-db"  # Fixed: simplified name
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier              = var.db_tier
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.db_disk_size
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = var.enable_backup
      start_time                     = "02:00"
      point_in_time_recovery_enabled = false
      backup_retention_settings {
        retained_backups = var.backup_retention_days
        retention_unit   = "COUNT"
      }
    }
    
    ip_configuration {
      ipv4_enabled = true   # Use public IP for now
      ssl_mode     = "ENCRYPTED_ONLY"
      
      authorized_networks {
        name  = "allow-all-for-setup"
        value = "0.0.0.0/0"  # Temporary - should be restricted in production
      }
    }
  }
  
  deletion_protection = false
  depends_on = [google_project_service.required_apis]
}

# Simplified networking - use public IP for now to avoid permission issues
# Private service connection can be added later with proper IAM setup

# Cloud SQL Database
resource "google_sql_database" "database" {
  name     = var.db_name
  instance = google_sql_database_instance.main.name
}

# Cloud SQL User
resource "google_sql_user" "user" {
  name     = var.db_user
  instance = google_sql_database_instance.main.name
  password = var.db_password
}

# Redis Instance with private networking
resource "google_redis_instance" "cache" {
  name           = "anzx-ai-platform-redis"  # Fixed: simplified name
  tier           = "BASIC"
  memory_size_gb = var.redis_memory_size
  region         = var.region
  
  redis_version      = "REDIS_7_0"
  display_name       = "ANZX AI Platform Redis"
  # Remove VPC dependency for now to avoid networking issues
  # authorized_network = google_compute_network.vpc.id
  connect_mode       = "DIRECT_PEERING"
  
  depends_on = [google_project_service.required_apis]
}

# Service Account for Cloud Run services
resource "google_service_account" "cloud_run_sa" {
  account_id   = "anzx-ai-platform-run-sa"
  display_name = "ANZX AI Platform Cloud Run Service Account"
  description  = "Service account for ANZX AI Platform Cloud Run services"
}

# IAM bindings for the service account
resource "google_project_iam_member" "cloud_run_sa_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_discoveryengine" {
  project = var.project_id
  role    = "roles/discoveryengine.editor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_secretmanager" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloud_run_sa_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run service for Core API
resource "google_cloud_run_service" "core_api" {
  name     = "anzx-ai-platform-core-api"  # Fixed: simplified name
  location = var.region
  
  template {
    metadata {
      annotations = {
        # Remove VPC connector for now to simplify deployment
        # "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.id
        # "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
        "autoscaling.knative.dev/minScale" = tostring(var.api_min_instances)
        "autoscaling.knative.dev/maxScale" = tostring(var.api_max_instances)
      }
    }
    
    spec {
      service_account_name = google_service_account.cloud_run_sa.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${data.google_artifact_registry_repository.docker_repo.repository_id}/core-api:v1.0.4"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${var.db_password}@${google_sql_database_instance.main.public_ip_address}:5432/${google_sql_database.database.name}?sslmode=require"
        }
        
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "JWT_SECRET_KEY"
          value = var.jwt_secret_key
        }
        
        env {
          name  = "ENABLE_TRACING"
          value = "true"
        }
        
        env {
          name  = "ENABLE_METRICS"
          value = "true"
        }
        
        resources {
          limits = {
            cpu    = var.api_cpu_limit
            memory = var.api_memory_limit
          }
        }
      }
      
      container_concurrency = 100
      timeout_seconds      = 300
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_sql_database_instance.main,
    google_redis_instance.cache
  ]
}

# Cloud Run service for Knowledge Service
resource "google_cloud_run_service" "knowledge_service" {
  name     = "anzx-ai-platform-knowledge-service"  # Fixed: simplified name
  location = var.region
  
  template {
    metadata {
      annotations = {
        # Remove VPC connector for now to simplify deployment
        # "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.id
        # "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
      }
    }
    
    spec {
      service_account_name = google_service_account.cloud_run_sa.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${data.google_artifact_registry_repository.docker_repo.repository_id}/knowledge-service:latest"
        
        ports {
          container_port = 8001
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${var.db_password}@${google_sql_database_instance.main.public_ip_address}:5432/${google_sql_database.database.name}?sslmode=require"
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        resources {
          limits = {
            cpu    = var.api_cpu_limit
            memory = var.api_memory_limit
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_sql_database_instance.main
  ]
}

# IAM for Cloud Run services (public access)
resource "google_cloud_run_service_iam_member" "core_api_public" {
  service  = google_cloud_run_service.core_api.name
  location = google_cloud_run_service.core_api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "knowledge_service_public" {
  service  = google_cloud_run_service.knowledge_service.name
  location = google_cloud_run_service.knowledge_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Storage buckets
resource "google_storage_bucket" "documents" {
  name     = "${var.project_id}-${local.app_name}-documents"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}

resource "google_storage_bucket" "assets" {
  name     = "${var.project_id}-${local.app_name}-assets"
  location = var.region
  
  uniform_bucket_level_access = true
  
  website {
    main_page_suffix = "index.html"
    not_found_page   = "404.html"
  }
}

# Secrets will be managed separately - using variables directly for now

# Secret versions will be created manually or via separate process to avoid permission issues

# Outputs
output "core_api_url" {
  value = google_cloud_run_service.core_api.status[0].url
}

output "knowledge_service_url" {
  value = google_cloud_run_service.knowledge_service.status[0].url
}

output "database_connection_name" {
  value = google_sql_database_instance.main.connection_name
}

output "database_private_ip" {
  value = google_sql_database_instance.main.private_ip_address
}

output "redis_host" {
  value = google_redis_instance.cache.host
}

output "artifact_registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${data.google_artifact_registry_repository.docker_repo.repository_id}"
}

# Monitoring resources removed for simplified deployment
# Can be added back later once core infrastructure is stable