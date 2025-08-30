# Cloud Build triggers for CI/CD
resource "google_cloudbuild_trigger" "core_api" {
  name        = "${local.name_prefix}-core-api-trigger"
  description = "Build and deploy Core API service"
  
  github {
    owner = "your-github-org"  # Replace with actual GitHub org
    name  = "anzx-ai-virtual-agents"
    
    push {
      branch = var.environment == "prod" ? "^main$" : "^develop$"
    }
  }
  
  included_files = [
    "services/core-api/**",
    "infrastructure/cloudbuild/core-api.yaml"
  ]
  
  filename = "infrastructure/cloudbuild/core-api.yaml"
  
  substitutions = {
    _ENVIRONMENT = var.environment
    _REGION      = var.region
    _PROJECT_ID  = var.project_id
    _REPO_NAME   = google_artifact_registry_repository.repo.repository_id
    _SERVICE_NAME = google_cloud_run_service.core_api.name
  }
  
  service_account = google_service_account.build_service_account.id
  
  depends_on = [time_sleep.wait_for_apis]
}

resource "google_cloudbuild_trigger" "agent_orchestration" {
  name        = "${local.name_prefix}-agent-orchestration-trigger"
  description = "Build and deploy Agent Orchestration service"
  
  github {
    owner = "your-github-org"  # Replace with actual GitHub org
    name  = "anzx-ai-virtual-agents"
    
    push {
      branch = var.environment == "prod" ? "^main$" : "^develop$"
    }
  }
  
  included_files = [
    "services/agent-orchestration/**",
    "infrastructure/cloudbuild/agent-orchestration.yaml"
  ]
  
  filename = "infrastructure/cloudbuild/agent-orchestration.yaml"
  
  substitutions = {
    _ENVIRONMENT = var.environment
    _REGION      = var.region
    _PROJECT_ID  = var.project_id
    _REPO_NAME   = google_artifact_registry_repository.repo.repository_id
    _SERVICE_NAME = google_cloud_run_service.agent_orchestration.name
  }
  
  service_account = google_service_account.build_service_account.id
}

resource "google_cloudbuild_trigger" "knowledge_service" {
  name        = "${local.name_prefix}-knowledge-service-trigger"
  description = "Build and deploy Knowledge Service"
  
  github {
    owner = "your-github-org"  # Replace with actual GitHub org
    name  = "anzx-ai-virtual-agents"
    
    push {
      branch = var.environment == "prod" ? "^main$" : "^develop$"
    }
  }
  
  included_files = [
    "services/knowledge-service/**",
    "infrastructure/cloudbuild/knowledge-service.yaml"
  ]
  
  filename = "infrastructure/cloudbuild/knowledge-service.yaml"
  
  substitutions = {
    _ENVIRONMENT = var.environment
    _REGION      = var.region
    _PROJECT_ID  = var.project_id
    _REPO_NAME   = google_artifact_registry_repository.repo.repository_id
    _SERVICE_NAME = google_cloud_run_service.knowledge_service.name
  }
  
  service_account = google_service_account.build_service_account.id
}

resource "google_cloudbuild_trigger" "chat_widget" {
  name        = "${local.name_prefix}-chat-widget-trigger"
  description = "Build and deploy Chat Widget"
  
  github {
    owner = "your-github-org"  # Replace with actual GitHub org
    name  = "anzx-ai-virtual-agents"
    
    push {
      branch = var.environment == "prod" ? "^main$" : "^develop$"
    }
  }
  
  included_files = [
    "services/chat-widget/**",
    "infrastructure/cloudbuild/chat-widget.yaml"
  ]
  
  filename = "infrastructure/cloudbuild/chat-widget.yaml"
  
  substitutions = {
    _ENVIRONMENT = var.environment
    _REGION      = var.region
    _PROJECT_ID  = var.project_id
    _ASSETS_BUCKET = google_storage_bucket.assets.name
  }
  
  service_account = google_service_account.build_service_account.id
}