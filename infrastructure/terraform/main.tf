terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "anzx-terraform-state"
    prefix = "platform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Local values for resource naming
locals {
  name_prefix = "${var.environment}-anzx"
  
  common_labels = {
    environment = var.environment
    project     = "anzx-ai-platform"
    managed_by  = "terraform"
  }
}