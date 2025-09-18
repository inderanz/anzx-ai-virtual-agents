# ANZX AI Platform - Production Infrastructure
# Terraform configuration for Google Cloud Platform deployment

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "anzx-ai-terraform-state"
    prefix = "production"
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Local values for resource naming
locals {
  environment = "production"
  app_name    = "anzx-ai-platform"
  
  common_labels = {
    environment = local.environment
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
    "sql.googleapis.com",
    "redis.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "aiplatform.googleapis.com",
    "documentai.googleapis.com"
  ])
  
  service = each.value
  project = var.project_id
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

# VPC Network
resource "google_compute_network" "vpc" {
  name                    = "${local.app_name}-vpc"
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.required_apis]
}

# Subnet for GKE cluster
resource "google_compute_subnetwork" "gke_subnet" {
  name          = "${local.app_name}-gke-subnet"
  ip_cidr_range = "10.1.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc.id
  
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.2.0.0/16"
  }
  
  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.3.0.0/16"
  }
}

# Subnet for Cloud SQL
resource "google_compute_subnetwork" "db_subnet" {
  name          = "${local.app_name}-db-subnet"
  ip_cidr_range = "10.4.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc.id
}

# Cloud NAT for outbound internet access
resource "google_compute_router" "router" {
  name    = "${local.app_name}-router"
  region  = var.region
  network = google_compute_network.vpc.id
}

resource "google_compute_router_nat" "nat" {
  name                               = "${local.app_name}-nat"
  router                            = google_compute_router.router.name
  region                            = var.region
  nat_ip_allocate_option            = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  
  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "${local.app_name}-allow-internal"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }
  
  allow {
    protocol = "icmp"
  }
  
  source_ranges = ["10.0.0.0/8"]
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "${local.app_name}-allow-health-checks"
  network = google_compute_network.vpc.name
  
  allow {
    protocol = "tcp"
    ports    = ["8080", "8000", "3000"]
  }
  
  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]
  
  target_tags = ["http-server"]
}

# GKE Cluster for blue-green deployments
resource "google_container_cluster" "primary" {
  name     = "${local.app_name}-gke"
  location = var.region
  
  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1
  
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.gke_subnet.name
  
  # IP allocation policy
  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"
    services_secondary_range_name = "services"
  }
  
  # Network policy
  network_policy {
    enabled = true
  }
  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  # Master authorized networks
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks"
    }
  }
  
  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    
    horizontal_pod_autoscaling {
      disabled = false
    }
    
    network_policy_config {
      disabled = false
    }
  }
  
  # Maintenance policy
  maintenance_policy {
    recurring_window {
      start_time = "2023-01-01T02:00:00Z"
      end_time   = "2023-01-01T06:00:00Z"
      recurrence = "FREQ=WEEKLY;BYDAY=SA"
    }
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_compute_subnetwork.gke_subnet
  ]
}

# GKE Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${local.app_name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.gke_num_nodes
  
  node_config {
    preemptible  = false
    machine_type = var.gke_machine_type
    
    # Google recommends custom service accounts with minimal permissions
    service_account = google_service_account.gke_service_account.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    labels = local.common_labels
    
    tags = ["gke-node", "${local.app_name}-gke"]
    
    metadata = {
      disable-legacy-endpoints = "true"
    }
    
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }
  
  # Auto-scaling
  autoscaling {
    min_node_count = var.gke_min_nodes
    max_node_count = var.gke_max_nodes
  }
  
  # Auto-upgrade and auto-repair
  management {
    auto_repair  = true
    auto_upgrade = true
  }
  
  depends_on = [google_container_cluster.primary]
}

# Service Account for GKE nodes
resource "google_service_account" "gke_service_account" {
  account_id   = "${local.app_name}-gke-sa"
  display_name = "GKE Service Account"
  description  = "Service account for GKE nodes"
}

# IAM bindings for GKE service account
resource "google_project_iam_member" "gke_service_account_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/monitoring.viewer",
    "roles/stackdriver.resourceMetadata.writer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.gke_service_account.email}"
}

# Cloud SQL Instance
resource "google_sql_database_instance" "main" {
  name             = "${local.app_name}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier              = var.db_tier
    availability_type = "REGIONAL"
    disk_type         = "PD_SSD"
    disk_size         = var.db_disk_size
    disk_autoresize   = true
    
    backup_configuration {
      enabled                        = true
      start_time                     = "02:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.id
      require_ssl     = true
    }
    
    database_flags {
      name  = "shared_preload_libraries"
      value = "vector"
    }
    
    maintenance_window {
      day          = 7
      hour         = 2
      update_track = "stable"
    }
  }
  
  deletion_protection = true
  
  depends_on = [
    google_project_service.required_apis,
    google_service_networking_connection.private_vpc_connection
  ]
}

# Private VPC connection for Cloud SQL
resource "google_compute_global_address" "private_ip_address" {
  name          = "${local.app_name}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]
}

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

# Redis Instance
resource "google_redis_instance" "cache" {
  name           = "${local.app_name}-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = var.redis_memory_size
  region         = var.region
  
  authorized_network = google_compute_network.vpc.id
  
  redis_version     = "REDIS_7_0"
  display_name      = "ANZX AI Platform Redis"
  
  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours   = 2
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }
  
  depends_on = [google_project_service.required_apis]
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = "${local.app_name}-docker"
  description   = "Docker repository for ANZX AI Platform"
  format        = "DOCKER"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Run services for API
resource "google_cloud_run_service" "api" {
  name     = "${local.app_name}-api"
  location = var.region
  
  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}/core-api:latest"
        
        ports {
          container_port = 8000
        }
        
        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.user.name}:${var.db_password}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.database.name}"
        }
        
        env {
          name  = "REDIS_URL"
          value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
        }
        
        env {
          name  = "ENVIRONMENT"
          value = "production"
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
      
      container_concurrency = 100
      timeout_seconds      = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "2"
        "autoscaling.knative.dev/maxScale" = "100"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.name
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    google_project_service.required_apis,
    google_vpc_access_connector.connector
  ]
}

# VPC Access Connector for Cloud Run
resource "google_vpc_access_connector" "connector" {
  name          = "${local.app_name}-connector"
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.vpc.name
  region        = var.region
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Run IAM
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.api.name
  location = google_cloud_run_service.api.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Load Balancer
resource "google_compute_global_address" "lb_ip" {
  name = "${local.app_name}-lb-ip"
}

resource "google_compute_managed_ssl_certificate" "ssl_cert" {
  name = "${local.app_name}-ssl-cert"
  
  managed {
    domains = [var.domain_name]
  }
}

# Secret Manager secrets
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${local.app_name}-db-password"
  
  replication {
    automatic = true
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${local.app_name}-jwt-secret"
  
  replication {
    automatic = true
  }
  
  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = var.jwt_secret_key
}

# Monitoring and Alerting
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification Channel"
  type         = "email"
  
  labels = {
    email_address = var.alert_email
  }
}

resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Cloud Run Error Rate"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${google_cloud_run_service.api.name}\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "300s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Build trigger for CI/CD
resource "google_cloudbuild_trigger" "main_branch" {
  name        = "${local.app_name}-main-deploy"
  description = "Deploy to production on main branch push"
  
  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }
  
  filename = "cloudbuild.yaml"
  
  depends_on = [google_project_service.required_apis]
}