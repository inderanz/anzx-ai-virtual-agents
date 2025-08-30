# Global Load Balancer with SSL certificates for TLS 1.2+
resource "google_compute_global_address" "lb_ip" {
  name = "${local.name_prefix}-lb-ip"
}

# SSL certificate for the domain
resource "google_compute_managed_ssl_certificate" "ssl_cert" {
  name = "${local.name_prefix}-ssl-cert"
  
  managed {
    domains = [
      var.domain_name,
      "www.${var.domain_name}",
      "api.${var.domain_name}",
      "widget.${var.domain_name}"
    ]
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# URL map for routing
resource "google_compute_url_map" "url_map" {
  name            = "${local.name_prefix}-url-map"
  default_service = google_compute_backend_service.core_api.id
  
  host_rule {
    hosts        = ["api.${var.domain_name}"]
    path_matcher = "api-paths"
  }
  
  host_rule {
    hosts        = ["widget.${var.domain_name}"]
    path_matcher = "widget-paths"
  }
  
  path_matcher {
    name            = "api-paths"
    default_service = google_compute_backend_service.core_api.id
    
    path_rule {
      paths   = ["/agent/*"]
      service = google_compute_backend_service.agent_orchestration.id
    }
    
    path_rule {
      paths   = ["/knowledge/*"]
      service = google_compute_backend_service.knowledge_service.id
    }
  }
  
  path_matcher {
    name            = "widget-paths"
    default_service = google_compute_backend_bucket.widget_bucket.id
  }
}

# Backend services for Cloud Run
resource "google_compute_backend_service" "core_api" {
  name                  = "${local.name_prefix}-core-api-backend"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 30
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL"
  
  backend {
    group = google_compute_region_network_endpoint_group.core_api_neg.id
  }
  
  security_policy = google_compute_security_policy.security_policy.id
  
  log_config {
    enable      = true
    sample_rate = 1.0
  }
  
  iap {
    oauth2_client_id     = var.environment == "prod" ? google_iap_client.iap_client[0].client_id : ""
    oauth2_client_secret = var.environment == "prod" ? google_iap_client.iap_client[0].secret : ""
  }
}

resource "google_compute_backend_service" "agent_orchestration" {
  name                  = "${local.name_prefix}-agent-orchestration-backend"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 60
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL"
  
  backend {
    group = google_compute_region_network_endpoint_group.agent_orchestration_neg.id
  }
  
  security_policy = google_compute_security_policy.security_policy.id
}

resource "google_compute_backend_service" "knowledge_service" {
  name                  = "${local.name_prefix}-knowledge-service-backend"
  protocol              = "HTTP"
  port_name             = "http"
  timeout_sec           = 300
  enable_cdn            = false
  load_balancing_scheme = "EXTERNAL"
  
  backend {
    group = google_compute_region_network_endpoint_group.knowledge_service_neg.id
  }
  
  security_policy = google_compute_security_policy.security_policy.id
}

# Network Endpoint Groups for Cloud Run services
resource "google_compute_region_network_endpoint_group" "core_api_neg" {
  name                  = "${local.name_prefix}-core-api-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  
  cloud_run {
    service = google_cloud_run_service.core_api.name
  }
}

resource "google_compute_region_network_endpoint_group" "agent_orchestration_neg" {
  name                  = "${local.name_prefix}-agent-orchestration-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  
  cloud_run {
    service = google_cloud_run_service.agent_orchestration.name
  }
}

resource "google_compute_region_network_endpoint_group" "knowledge_service_neg" {
  name                  = "${local.name_prefix}-knowledge-service-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  
  cloud_run {
    service = google_cloud_run_service.knowledge_service.name
  }
}

# Backend bucket for chat widget
resource "google_compute_backend_bucket" "widget_bucket" {
  name        = "${local.name_prefix}-widget-backend"
  bucket_name = google_storage_bucket.assets.name
  enable_cdn  = true
  
  cdn_policy {
    cache_mode                   = "CACHE_ALL_STATIC"
    default_ttl                  = 3600
    max_ttl                      = 86400
    negative_caching             = true
    serve_while_stale            = 86400
    signed_url_cache_max_age_sec = 7200
  }
}

# HTTPS proxy
resource "google_compute_target_https_proxy" "https_proxy" {
  name             = "${local.name_prefix}-https-proxy"
  url_map          = google_compute_url_map.url_map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.ssl_cert.id]
  
  # Enforce TLS 1.2+
  ssl_policy = google_compute_ssl_policy.ssl_policy.id
}

# SSL Policy for TLS 1.2+
resource "google_compute_ssl_policy" "ssl_policy" {
  name            = "${local.name_prefix}-ssl-policy"
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
}

# Global forwarding rule
resource "google_compute_global_forwarding_rule" "https_forwarding_rule" {
  name       = "${local.name_prefix}-https-forwarding-rule"
  target     = google_compute_target_https_proxy.https_proxy.id
  port_range = "443"
  ip_address = google_compute_global_address.lb_ip.address
}

# HTTP to HTTPS redirect
resource "google_compute_url_map" "http_redirect" {
  name = "${local.name_prefix}-http-redirect"
  
  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "http_proxy" {
  name    = "${local.name_prefix}-http-proxy"
  url_map = google_compute_url_map.http_redirect.id
}

resource "google_compute_global_forwarding_rule" "http_forwarding_rule" {
  name       = "${local.name_prefix}-http-forwarding-rule"
  target     = google_compute_target_http_proxy.http_proxy.id
  port_range = "80"
  ip_address = google_compute_global_address.lb_ip.address
}

# Cloud Armor security policy
resource "google_compute_security_policy" "security_policy" {
  name = "${local.name_prefix}-security-policy"
  
  # Default rule - allow all
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }
  
  # Rate limiting rule
  rule {
    action   = "rate_based_ban"
    priority = "1000"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"
      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
      ban_duration_sec = 300
    }
    description = "Rate limiting rule"
  }
  
  # Block known bad IPs
  rule {
    action   = "deny(403)"
    priority = "900"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = [
          "10.0.0.0/8",     # Private networks
          "172.16.0.0/12",  # Private networks
          "192.168.0.0/16"  # Private networks
        ]
      }
    }
    description = "Block private IP ranges"
  }
  
  # OWASP ModSecurity Core Rule Set
  rule {
    action   = "deny(403)"
    priority = "800"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block XSS attacks"
  }
  
  rule {
    action   = "deny(403)"
    priority = "700"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "Block SQL injection attacks"
  }
}

# Identity-Aware Proxy for production
resource "google_iap_client" "iap_client" {
  count = var.environment == "prod" ? 1 : 0
  
  display_name = "ANZx.ai Platform IAP Client"
  brand        = google_iap_brand.project_brand[0].name
}

resource "google_iap_brand" "project_brand" {
  count = var.environment == "prod" ? 1 : 0
  
  support_email     = "support@${var.domain_name}"
  application_title = "ANZx.ai Platform"
  project           = var.project_id
}