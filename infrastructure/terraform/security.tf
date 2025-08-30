# Cloud KMS for encryption key management
resource "google_kms_key_ring" "key_ring" {
  name     = "${local.name_prefix}-keyring"
  location = var.region
  
  depends_on = [time_sleep.wait_for_apis]
}

# Application encryption key
resource "google_kms_crypto_key" "app_key" {
  name     = "${local.name_prefix}-app-key"
  key_ring = google_kms_key_ring.key_ring.id
  purpose  = "ENCRYPT_DECRYPT"
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Database encryption key
resource "google_kms_crypto_key" "db_key" {
  name     = "${local.name_prefix}-db-key"
  key_ring = google_kms_key_ring.key_ring.id
  purpose  = "ENCRYPT_DECRYPT"
  
  version_template {
    algorithm = "GOOGLE_SYMMETRIC_ENCRYPTION"
  }
  
  rotation_period = "7776000s"  # 90 days
  
  lifecycle {
    prevent_destroy = true
  }
}

# Service account for applications
resource "google_service_account" "app_service_account" {
  account_id   = "${local.name_prefix}-app-sa"
  display_name = "ANZx.ai Application Service Account"
  description  = "Service account for ANZx.ai platform services"
}

# Service account for Cloud Build
resource "google_service_account" "build_service_account" {
  account_id   = "${local.name_prefix}-build-sa"
  display_name = "ANZx.ai Build Service Account"
  description  = "Service account for Cloud Build CI/CD"
}

# IAM roles for application service account
resource "google_project_iam_member" "app_sa_roles" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/redis.editor",
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/cloudkms.cryptoKeyEncrypterDecrypter",
    "roles/aiplatform.user",
    "roles/documentai.apiUser",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/errorreporting.writer"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.app_service_account.email}"
}

# IAM roles for build service account
resource "google_project_iam_member" "build_sa_roles" {
  for_each = toset([
    "roles/cloudbuild.builds.builder",
    "roles/run.admin",
    "roles/storage.admin",
    "roles/artifactregistry.admin",
    "roles/secretmanager.admin",
    "roles/iam.serviceAccountUser"
  ])
  
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.build_service_account.email}"
}

# Secret Manager secrets
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${local.name_prefix}-db-password"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
  
  depends_on = [time_sleep.wait_for_apis]
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${local.name_prefix}-jwt-secret"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

resource "random_password" "jwt_secret" {
  length  = 64
  special = true
}

# Firebase project configuration (placeholder)
resource "google_secret_manager_secret" "firebase_config" {
  secret_id = "${local.name_prefix}-firebase-config"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

# Stripe API keys (to be set manually)
resource "google_secret_manager_secret" "stripe_secret_key" {
  secret_id = "${local.name_prefix}-stripe-secret-key"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "stripe_webhook_secret" {
  secret_id = "${local.name_prefix}-stripe-webhook-secret"
  
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}