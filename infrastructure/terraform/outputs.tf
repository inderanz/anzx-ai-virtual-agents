output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}

# Database outputs
output "database_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.postgres.name
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "database_private_ip" {
  description = "Database private IP address"
  value       = google_sql_database_instance.postgres.private_ip_address
  sensitive   = true
}

# Redis outputs
output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.cache.host
  sensitive   = true
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.cache.port
}

# Cloud Run service URLs
output "core_api_url" {
  description = "Core API service URL"
  value       = google_cloud_run_service.core_api.status[0].url
}

output "agent_orchestration_url" {
  description = "Agent Orchestration service URL"
  value       = google_cloud_run_service.agent_orchestration.status[0].url
}

output "knowledge_service_url" {
  description = "Knowledge Service URL"
  value       = google_cloud_run_service.knowledge_service.status[0].url
}

# Storage buckets
output "documents_bucket" {
  description = "Documents storage bucket name"
  value       = google_storage_bucket.documents.name
}

output "assets_bucket" {
  description = "Assets storage bucket name"
  value       = google_storage_bucket.assets.name
}

output "backups_bucket" {
  description = "Backups storage bucket name"
  value       = google_storage_bucket.backups.name
}

# Container registry
output "artifact_registry_repository" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}"
}

# Service accounts
output "app_service_account_email" {
  description = "Application service account email"
  value       = google_service_account.app_service_account.email
}

output "build_service_account_email" {
  description = "Build service account email"
  value       = google_service_account.build_service_account.email
}

# Security
output "kms_key_ring" {
  description = "KMS key ring name"
  value       = google_kms_key_ring.key_ring.name
}

output "app_encryption_key" {
  description = "Application encryption key name"
  value       = google_kms_crypto_key.app_key.name
}

# Networking
output "vpc_network" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "vpc_connector" {
  description = "VPC connector name"
  value       = google_vpc_access_connector.connector.name
}

# Monitoring
output "monitoring_dashboard_url" {
  description = "Monitoring dashboard URL"
  value       = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.main.id}?project=${var.project_id}"
}