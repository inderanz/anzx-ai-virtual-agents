# Monitoring and alerting configuration
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notifications"
  type         = "email"
  
  labels = {
    email_address = "alerts@${var.domain_name}"
  }
  
  depends_on = [time_sleep.wait_for_apis]
}

resource "google_monitoring_notification_channel" "slack" {
  count = var.environment == "prod" ? 1 : 0
  
  display_name = "Slack Notifications"
  type         = "slack"
  
  labels = {
    channel_name = "#alerts"
    url          = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
  }
  
  sensitive_labels {
    auth_token = "your-slack-token"
  }
}

# SLO for API availability
resource "google_monitoring_slo" "api_availability" {
  service      = google_monitoring_service.core_api.service_id
  display_name = "Core API Availability SLO"
  
  request_based_sli {
    good_total_ratio {
      total_service_filter = "resource.type=\"cloud_run_revision\""
      good_service_filter  = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.labels.response_code_class=\"2xx\""
    }
  }
  
  goal = 0.999  # 99.9% availability
  
  rolling_period_days = 30
}

# SLO for API latency
resource "google_monitoring_slo" "api_latency" {
  service      = google_monitoring_service.core_api.service_id
  display_name = "Core API Latency SLO"
  
  request_based_sli {
    distribution_cut {
      distribution_filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
      
      range {
        max = 1000  # 1 second
      }
    }
  }
  
  goal = 0.95  # 95% of requests under 1s
  
  rolling_period_days = 30
}

# Custom service for monitoring
resource "google_monitoring_service" "core_api" {
  service_id   = "${local.name_prefix}-core-api"
  display_name = "ANZx.ai Core API"
  
  basic_service {
    service_type = "CLOUD_RUN"
    service_labels = {
      service_name = google_cloud_run_service.core_api.name
      location     = google_cloud_run_service.core_api.location
    }
  }
}

# Alert policies
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate"
  combiner     = "OR"
  
  conditions {
    display_name = "Error rate above 5%"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.05
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields = ["resource.label.service_name"]
      }
      
      trigger {
        count = 1
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
  
  alert_strategy {
    auto_close = "1800s"
  }
}

resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "High Latency"
  combiner     = "OR"
  
  conditions {
    display_name = "95th percentile latency above 2s"
    
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 2000
      
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
        group_by_fields      = ["resource.label.service_name"]
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
}

resource "google_monitoring_alert_policy" "database_cpu" {
  display_name = "Database High CPU"
  combiner     = "OR"
  
  conditions {
    display_name = "Database CPU above 80%"
    
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\""
      duration        = "300s"
      comparison      = "COMPARISON_GREATER_THAN"
      threshold_value = 0.8
      
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }
  
  notification_channels = [google_monitoring_notification_channel.email.name]
}

# Custom dashboard
resource "google_monitoring_dashboard" "main" {
  dashboard_json = jsonencode({
    displayName = "ANZx.ai Platform Dashboard"
    
    gridLayout = {
      widgets = [
        {
          title = "API Request Rate"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        },
        {
          title = "API Error Rate"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" AND metric.labels.response_code_class!=\"2xx\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Database Connections"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloudsql_database\" AND metric.type=\"cloudsql.googleapis.com/database/postgresql/num_backends\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Redis Memory Usage"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"redis_instance\" AND metric.type=\"redis.googleapis.com/stats/memory/usage_ratio\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
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