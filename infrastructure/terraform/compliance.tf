# Compliance and audit infrastructure
resource "google_logging_log_sink" "audit_sink" {
  name        = "${local.name_prefix}-audit-sink"
  destination = "storage.googleapis.com/${google_storage_bucket.audit_logs.name}"
  
  # Capture all audit logs
  filter = "protoPayload.serviceName=\"cloudaudit.googleapis.com\" OR labels.compliance=\"true\""
  
  unique_writer_identity = true
}

# Audit logs storage bucket
resource "google_storage_bucket" "audit_logs" {
  name          = "${var.project_id}-${var.environment}-audit-logs"
  location      = var.region
  force_destroy = var.environment != "prod"
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  # Retention policy for 7 years (Australian compliance requirement)
  lifecycle_rule {
    condition {
      age = 2555  # 7 years in days
    }
    action {
      type = "Delete"
    }
  }
  
  # Move to cheaper storage after 90 days
  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type          = "SetStorageClass"
      storage_class = "COLDLINE"
    }
  }
  
  # Encryption with customer-managed key
  encryption {
    default_kms_key_name = google_kms_crypto_key.audit_key.id
  }
}

# Dedicated encryption key for audit logs
resource "google_kms_crypto_key" "audit_key" {
  name     = "${local.name_prefix}-audit-key"
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

# IAM for audit log sink
resource "google_storage_bucket_iam_member" "audit_sink_writer" {
  bucket = google_storage_bucket.audit_logs.name
  role   = "roles/storage.objectCreator"
  member = google_logging_log_sink.audit_sink.writer_identity
}

# Privacy compliance monitoring
resource "google_monitoring_alert_policy" "privacy_violations" {
  display_name = "Privacy Compliance Violations"
  combiner     = "OR"
  
  conditions {
    display_name = "Unauthorized data access"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND jsonPayload.audit_event.risk_level=\"high\""
      duration        = "60s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
  
  alert_strategy {
    auto_close = "86400s"  # 24 hours
  }
}

# Data breach response alert
resource "google_monitoring_alert_policy" "data_breach" {
  display_name = "Data Breach Detected"
  combiner     = "OR"
  
  conditions {
    display_name = "Security incident reported"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND jsonPayload.audit_event.event_type=\"security_incident\""
      duration        = "0s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_COUNT"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
  
  alert_strategy {
    auto_close = "0s"  # Manual close required
  }
}

# Compliance dashboard
resource "google_monitoring_dashboard" "compliance" {
  dashboard_json = jsonencode({
    displayName = "ANZx.ai Compliance Dashboard"
    
    gridLayout = {
      widgets = [
        {
          title = "Privacy Requests"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.audit_event.event_type=\"privacy_request\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_COUNT"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Consent Events"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND (jsonPayload.audit_event.event_type=\"consent_given\" OR jsonPayload.audit_event.event_type=\"consent_withdrawn\")"
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_COUNT"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields = ["jsonPayload.audit_event.event_type"]
                  }
                }
              }
            }]
          }
        },
        {
          title = "High-Risk Events"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.audit_event.risk_level=\"high\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_COUNT"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Cross-Border Transfers"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.audit_event.event_type=\"cross_border_transfer\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_COUNT"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        }
      ]
    }
  })
}

# Binary Authorization for container security
resource "google_binary_authorization_policy" "policy" {
  count = var.environment == "prod" ? 1 : 0
  
  admission_whitelist_patterns {
    name_pattern = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.repo.repository_id}/*"
  }
  
  default_admission_rule {
    evaluation_mode  = "REQUIRE_ATTESTATION"
    enforcement_mode = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    
    require_attestations_by = [
      google_binary_authorization_attestor.attestor[0].name
    ]
  }
  
  cluster_admission_rules {
    cluster                 = "projects/${var.project_id}/locations/${var.region}/clusters/*"
    evaluation_mode        = "REQUIRE_ATTESTATION"
    enforcement_mode       = "ENFORCED_BLOCK_AND_AUDIT_LOG"
    require_attestations_by = [
      google_binary_authorization_attestor.attestor[0].name
    ]
  }
}

# Attestor for Binary Authorization
resource "google_binary_authorization_attestor" "attestor" {
  count = var.environment == "prod" ? 1 : 0
  
  name = "${local.name_prefix}-attestor"
  
  attestation_authority_note {
    note_reference = google_container_analysis_note.note[0].name
    
    public_keys {
      ascii_armored_pgp_public_key = file("${path.module}/attestor-public-key.pgp")
    }
  }
}

# Container Analysis note for attestations
resource "google_container_analysis_note" "note" {
  count = var.environment == "prod" ? 1 : 0
  
  name = "${local.name_prefix}-attestor-note"
  
  attestation_authority {
    hint {
      human_readable_name = "ANZx.ai Security Attestor"
    }
  }
}