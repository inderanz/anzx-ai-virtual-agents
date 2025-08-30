# Enable required Google Cloud APIs
resource "google_project_service" "apis" {
  for_each = toset(var.enable_apis)
  
  project = var.project_id
  service = each.value
  
  disable_dependent_services = false
  disable_on_destroy        = false
}

# Wait for APIs to be enabled before creating other resources
resource "time_sleep" "wait_for_apis" {
  depends_on = [google_project_service.apis]
  
  create_duration = "60s"
}