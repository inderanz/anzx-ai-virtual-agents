resource "google_cloudbuild_trigger" "auth_frontend_trigger" {
  name        = "auth-frontend-feature-branch"
  description = "Builds and deploys the auth-frontend service on push to feature branch"
  project     = var.project_id
  location    = "global"

  trigger_template {
    branch_name = "feature/enterprise-customer-setup"
    repo_name   = var.github_repo
  }

  substitutions = {
    _SERVICE_NAME = "auth-frontend-anzx-ai"
    _REGION       = var.region
  }

  build {
    steps {
      name = "gcr.io/cloud-builders/npm"
      args = ["install"]
    }
    steps {
      name = "gcr.io/cloud-builders/npm"
      args = ["run", "build"]
    }
    steps {
      name = "gcr.io/cloud-builders/npm"
      args = ["install", "-g", "firebase-tools"]
    }
    steps {
      name       = "gcr.io/cloud-builders/npm"
      entrypoint = "firebase"
      args       = ["deploy", "--only", "hosting", "--project", var.project_id, "--non-interactive", "--token", "$SECRETS.FIREBASE_TOKEN"]
      secret_env = ["FIREBASE_TOKEN"]
    }

    secrets {
      secret_manager {
        version_name = "projects/${var.project_id}/secrets/firebase-token/versions/latest"
        env          = "FIREBASE_TOKEN"
      }
    }
  }
}
