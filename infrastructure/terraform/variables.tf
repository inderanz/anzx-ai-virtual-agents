# Terraform Variables for ANZX AI Platform

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "australia-southeast1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "australia-southeast1-a"
}

variable "domain_name" {
  description = "The domain name for the application"
  type        = string
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "alert_email" {
  description = "Email address for monitoring alerts"
  type        = string
}

# Database variables
variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "anzx_ai_platform"
}

variable "db_user" {
  description = "The database user"
  type        = string
  default     = "anzx_user"
}

variable "db_password" {
  description = "The database password"
  type        = string
  sensitive   = true
}

variable "db_tier" {
  description = "The database tier"
  type        = string
  default     = "db-custom-2-8192"
}

variable "db_disk_size" {
  description = "The database disk size in GB"
  type        = number
  default     = 100
}

# Redis variables
variable "redis_memory_size" {
  description = "Redis memory size in GB"
  type        = number
  default     = 4
}

# GKE variables
variable "gke_num_nodes" {
  description = "Number of GKE nodes"
  type        = number
  default     = 3
}

variable "gke_min_nodes" {
  description = "Minimum number of GKE nodes"
  type        = number
  default     = 1
}

variable "gke_max_nodes" {
  description = "Maximum number of GKE nodes"
  type        = number
  default     = 10
}

variable "gke_machine_type" {
  description = "GKE node machine type"
  type        = string
  default     = "e2-standard-4"
}

# Security variables
variable "jwt_secret_key" {
  description = "JWT secret key"
  type        = string
  sensitive   = true
}

variable "stripe_secret_key" {
  description = "Stripe secret key"
  type        = string
  sensitive   = true
}

# Removed OpenAI - using Vertex AI instead

variable "vertex_ai_project" {
  description = "Vertex AI project ID"
  type        = string
}

# Environment-specific variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "enable_monitoring" {
  description = "Enable monitoring and alerting"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

# Scaling variables
variable "api_min_instances" {
  description = "Minimum number of API instances"
  type        = number
  default     = 2
}

variable "api_max_instances" {
  description = "Maximum number of API instances"
  type        = number
  default     = 100
}

variable "api_cpu_limit" {
  description = "CPU limit for API containers"
  type        = string
  default     = "2000m"
}

variable "api_memory_limit" {
  description = "Memory limit for API containers"
  type        = string
  default     = "4Gi"
}

# Network variables
variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "gke_subnet_cidr" {
  description = "CIDR block for GKE subnet"
  type        = string
  default     = "10.1.0.0/16"
}

variable "db_subnet_cidr" {
  description = "CIDR block for database subnet"
  type        = string
  default     = "10.4.0.0/24"
}

# Feature flags
variable "enable_blue_green_deployment" {
  description = "Enable blue-green deployment strategy"
  type        = bool
  default     = true
}

variable "enable_auto_scaling" {
  description = "Enable auto-scaling"
  type        = bool
  default     = true
}

variable "enable_ssl" {
  description = "Enable SSL/TLS"
  type        = bool
  default     = true
}

variable "enable_cdn" {
  description = "Enable CDN"
  type        = bool
  default     = true
}

# Compliance variables
variable "enable_audit_logs" {
  description = "Enable audit logging"
  type        = bool
  default     = true
}

variable "data_location_restriction" {
  description = "Restrict data to specific locations"
  type        = string
  default     = "australia-southeast1"
}

variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest"
  type        = bool
  default     = true
}

variable "enable_private_cluster" {
  description = "Enable private GKE cluster"
  type        = bool
  default     = true
}

# Observability variables
variable "enable_tracing" {
  description = "Enable distributed tracing"
  type        = bool
  default     = true
}

variable "enable_metrics" {
  description = "Enable metrics collection"
  type        = bool
  default     = true
}

variable "enable_alerting" {
  description = "Enable alerting"
  type        = bool
  default     = true
}