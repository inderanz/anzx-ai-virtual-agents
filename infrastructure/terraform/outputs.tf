# Terraform Outputs for ANZX AI Platform

output "project_id" {
  description = "GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP region"
  value       = var.region
}

# Network outputs
output "vpc_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "vpc_id" {
  description = "VPC network ID"
  value       = google_compute_network.vpc.id
}

output "gke_subnet_name" {
  description = "GKE subnet name"
  value       = google_compute_subnetwork.gke_subnet.name
}

output "db_subnet_name" {
  description = "Database subnet name"
  value       = google_compute_subnetwork.db_subnet.name
}

# GKE outputs
output "gke_cluster_name" {
  description = "GKE cluster name"
  value       = google_container_cluster.primary.name
}

output "gke_cluster_endpoint" {
  description = "GKE cluster endpoint"
  value       = google_container_cluster.primary.endpoint
  sensitive   = true
}

output "gke_cluster_ca_certificate" {
  description = "GKE cluster CA certificate"
  value       = google_container_cluster.primary.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "gke_service_account_email" {
  description = "GKE service account email"
  value       = google_service_account.gke_service_account.email
}

# Database outputs
output "db_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "db_instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "db_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.main.private_ip_address
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.database.name
}

output "database_user" {
  description = "Database user"
  value       = google_sql_user.user.name
}

# Redis outputs
output "redis_host" {
  description = "Redis host"
  value       = google_redis_instance.cache.host
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = google_redis_instance.cache.port
}

output "redis_auth_string" {
  description = "Redis auth string"
  value       = google_redis_instance.cache.auth_string
  sensitive   = true
}

# Cloud Run outputs
output "api_service_url" {
  description = "Cloud Run API service URL"
  value       = google_cloud_run_service.api.status[0].url
}

output "api_service_name" {
  description = "Cloud Run API service name"
  value       = google_cloud_run_service.api.name
}

# Load Balancer outputs
output "load_balancer_ip" {
  description = "Load balancer IP address"
  value       = google_compute_global_address.lb_ip.address
}

output "ssl_certificate_name" {
  description = "SSL certificate name"
  value       = google_compute_managed_ssl_certificate.ssl_cert.name
}

# Artifact Registry outputs
output "docker_repository_url" {
  description = "Docker repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

# Secret Manager outputs
output "db_password_secret_name" {
  description = "Database password secret name"
  value       = google_secret_manager_secret.db_password.secret_id
}

output "jwt_secret_name" {
  description = "JWT secret name"
  value       = google_secret_manager_secret.jwt_secret.secret_id
}

# Monitoring outputs
output "notification_channel_name" {
  description = "Monitoring notification channel name"
  value       = google_monitoring_notification_channel.email.name
}

# VPC Access Connector outputs
output "vpc_connector_name" {
  description = "VPC access connector name"
  value       = google_vpc_access_connector.connector.name
}

# Cloud Build outputs
output "cloudbuild_trigger_name" {
  description = "Cloud Build trigger name"
  value       = google_cloudbuild_trigger.main_branch.name
}

# Connection strings and URLs for applications
output "database_url" {
  description = "Database connection URL"
  value       = "postgresql://${google_sql_user.user.name}:${var.db_password}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.database.name}"
  sensitive   = true
}

output "redis_url" {
  description = "Redis connection URL"
  value       = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
  sensitive   = true
}

# Kubernetes configuration
output "kubectl_config_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.primary.name} --region ${var.region} --project ${var.project_id}"
}

# Environment information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "deployment_timestamp" {
  description = "Deployment timestamp"
  value       = timestamp()
}