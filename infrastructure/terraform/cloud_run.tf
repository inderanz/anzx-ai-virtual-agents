# Artifact Registry for container images
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "${local.name_prefix}-repo"
  description   = "ANZx.ai Platform container images"
  format        = "DOCKER"
  
  depends_on = [time_sleep.wait_for_apis]
}

# Cloud Run service for Core API
resource "google_cloud_run_service" "core_api" {
  name     = "${local.name_prefix}-core-api"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = var.min_instances
        "autoscaling.knative.dev/maxScale"         = var.max_instances
        "run.googleapis.com/cloudsql-instances"    = google_sql_database_instance.postgres.connection_name
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.connector.name
        "run.googleapis.com/vpc-access-egress"     = "private-ranges-only"
      }
      
      labels = local.common_labels
    }
    
    spec {
      service_account_name = google_service_account.app_service_account.email
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/core-api:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_connection_string.secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name  = "REDIS_HOST"
          value = google_redis_instance.cache.host
        }
        
        env {
          name  = "REDIS_PORT"
          value = tostring(google_redis_instance.cache.port)
        }
        
        env {
          name = "JWT_SECRET"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.jwt_secret.secret_id
              key  = "latest"
            }
          }
        }
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
          requests = {
            cpu    = "1000m"
            memory = "1Gi"
          }
        }
        
        startup_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 10
          timeout_seconds       = 5
          period_seconds        = 10
          failure_threshold     = 3
        }
        
        liveness_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          initial_delay_seconds = 30
          timeout_seconds       = 5
          period_seconds        = 30
          failure_threshold     = 3
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.apis]
}

# Cloud Run service for Agent Orchestration
resource "google_cloud_run_service" "agent_orchestration" {
  name     = "${local.name_prefix}-agent-orchestration"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"        = var.min_instances
        "autoscaling.knative.dev/maxScale"        = var.max_instances
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.name
        "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
      }
      
      labels = local.common_labels
    }
    
    spec {
      service_account_name = google_service_account.app_service_account.email
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/agent-orchestration:latest"
        
        ports {
          container_port = 8001
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "CORE_API_URL"
          value = google_cloud_run_service.core_api.status[0].url
        }
        
        env {
          name  = "REDIS_HOST"
          value = google_redis_instance.cache.host
        }
        
        env {
          name  = "REDIS_PORT"
          value = tostring(google_redis_instance.cache.port)
        }
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
          requests = {
            cpu    = "1000m"
            memory = "2Gi"
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Run service for Knowledge Service
resource "google_cloud_run_service" "knowledge_service" {
  name     = "${local.name_prefix}-knowledge-service"
  location = var.region
  
  template {
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale"         = var.min_instances
        "autoscaling.knative.dev/maxScale"         = var.max_instances
        "run.googleapis.com/cloudsql-instances"    = google_sql_database_instance.postgres.connection_name
        "run.googleapis.com/vpc-access-connector"  = google_vpc_access_connector.connector.name
        "run.googleapis.com/vpc-access-egress"     = "private-ranges-only"
      }
      
      labels = local.common_labels
    }
    
    spec {
      service_account_name = google_service_account.app_service_account.email
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/knowledge-service:latest"
        
        ports {
          container_port = 8002
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_connection_string.secret_id
              key  = "latest"
            }
          }
        }
        
        env {
          name  = "REDIS_HOST"
          value = google_redis_instance.cache.host
        }
        
        env {
          name  = "DOCUMENTS_BUCKET"
          value = google_storage_bucket.documents.name
        }
        
        resources {
          limits = {
            cpu    = "4000m"
            memory = "8Gi"
          }
          requests = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM policy for public access to services (configure as needed)
resource "google_cloud_run_service_iam_member" "core_api_public" {
  location = google_cloud_run_service.core_api.location
  project  = google_cloud_run_service.core_api.project
  service  = google_cloud_run_service.core_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Database connection string secret
resource "google_secret_manager_secret" "db_connection_string" {
  secret_id = "${local.name_prefix}-db-connection-string"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "db_connection_string" {
  secret = google_secret_manager_secret.db_connection_string.id
  secret_data = "postgresql://${google_sql_user.app_user.name}:${random_password.db_password.result}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.app_db.name}"
}