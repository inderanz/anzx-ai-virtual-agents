#!/bin/bash
# Cloud Build Helper Scripts
# Provides idempotent functions for common GCP operations

set -euo pipefail

# Logging helper
log_action() {
    local action="$1"
    local status="$2"
    shift 2
    local extra="$*"
    echo "{\"action\": \"$action\", \"status\": \"$status\"${extra:+", $extra"}}"
}

# Enable a GCP API
ensure_api() {
    local api="$1"
    if gcloud services list --enabled --filter="name:$api" --format="value(name)" | grep -q "^$api$"; then
        log_action "ensure_api" "exists" "\"api\": \"$api\""
    else
        gcloud services enable "$api"
        log_action "ensure_api" "enabled" "\"api\": \"$api\""
    fi
}

# Ensure GCS bucket exists
ensure_bucket() {
    local bucket="$1"
    local project="${2:-}"
    local region="${3:-}"
    
    if gsutil ls -b "gs://$bucket" >/dev/null 2>&1; then
        log_action "ensure_bucket" "exists" "\"bucket\": \"$bucket\""
    else
        local cmd="gsutil mb"
        [[ -n "$project" ]] && cmd="$cmd -p $project"
        [[ -n "$region" ]] && cmd="$cmd -l $region"
        $cmd "gs://$bucket"
        log_action "ensure_bucket" "created" "\"bucket\": \"$bucket\""
    fi
}

# Ensure Artifact Registry repository exists
ensure_artifact_repo() {
    local repo="$1"
    local region="$2"
    local format="${3:-docker}"
    
    if gcloud artifacts repositories describe "$repo" --location="$region" >/dev/null 2>&1; then
        log_action "ensure_artifact_repo" "exists" "\"repo\": \"$repo\", \"region\": \"$region\""
    else
        gcloud artifacts repositories create "$repo" \
            --repository-format="$format" \
            --location="$region" \
            --description="Repository for $repo"
        log_action "ensure_artifact_repo" "created" "\"repo\": \"$repo\", \"region\": \"$region\""
    fi
}

# Ensure service account exists
ensure_sa() {
    local sa_name="$1"
    local display_name="${2:-$sa_name Service Account}"
    local description="${3:-Service account for $sa_name}"
    
    if gcloud iam service-accounts describe "$sa_name" >/dev/null 2>&1; then
        log_action "ensure_sa" "exists" "\"sa\": \"$sa_name\""
    else
        gcloud iam service-accounts create "$sa_name" \
            --display-name="$display_name" \
            --description="$description"
        log_action "ensure_sa" "created" "\"sa\": \"$sa_name\""
    fi
}

# Ensure IAM binding exists
ensure_iam_binding() {
    local project="$1"
    local member="$2"
    local role="$3"
    
    if gcloud projects get-iam-policy "$project" --flatten="bindings[].members" --format="table(bindings.role)" --filter="bindings.members:$member AND bindings.role:$role" | grep -q "$role"; then
        log_action "ensure_iam_binding" "exists" "\"member\": \"$member\", \"role\": \"$role\""
    else
        gcloud projects add-iam-policy-binding "$project" \
            --member="$member" \
            --role="$role"
        log_action "ensure_iam_binding" "created" "\"member\": \"$member\", \"role\": \"$role\""
    fi
}

# Ensure secret exists (create placeholder if missing)
ensure_secret() {
    local secret_name="$1"
    local placeholder_value="${2:-placeholder}"
    
    if gcloud secrets describe "$secret_name" >/dev/null 2>&1; then
        log_action "ensure_secret" "exists" "\"secret\": \"$secret_name\""
    else
        echo -n "$placeholder_value" | gcloud secrets create "$secret_name" --data-file=-
        log_action "ensure_secret" "created" "\"secret\": \"$secret_name\", \"note\": \"placeholder_data\""
    fi
}

# Ensure secret exists with random value
ensure_secret_random() {
    local secret_name="$1"
    local length="${2:-32}"
    
    if gcloud secrets describe "$secret_name" >/dev/null 2>&1; then
        log_action "ensure_secret" "exists" "\"secret\": \"$secret_name\""
    else
        local random_value=$(openssl rand -base64 "$length")
        echo -n "$random_value" | gcloud secrets create "$secret_name" --data-file=-
        log_action "ensure_secret" "created" "\"secret\": \"$secret_name\", \"note\": \"random_${length}_byte\""
    fi
}

# Ensure build trigger exists (create or update)
ensure_build_trigger() {
    local trigger_name="$1"
    local trigger_spec="$2"
    
    if gcloud builds triggers describe "$trigger_name" >/dev/null 2>&1; then
        # Update existing trigger
        gcloud builds triggers update "$trigger_name" \
            --build-config="$(jq -r '.filename' "$trigger_spec")" \
            --repo-name="$(jq -r '.github.name' "$trigger_spec")" \
            --repo-owner="$(jq -r '.github.owner' "$trigger_spec")" \
            --branch-pattern="$(jq -r '.github.push.branch' "$trigger_spec")" \
            --substitutions="$(jq -r '.substitutions | to_entries | map("\(.key)=\(.value)") | join(",")' "$trigger_spec")"
        log_action "ensure_build_trigger" "updated" "\"trigger\": \"$trigger_name\""
    else
        # Create new trigger
        gcloud builds triggers create github \
            --name="$trigger_name" \
            --build-config="$(jq -r '.filename' "$trigger_spec")" \
            --repo-name="$(jq -r '.github.name' "$trigger_spec")" \
            --repo-owner="$(jq -r '.github.owner' "$trigger_spec")" \
            --branch-pattern="$(jq -r '.github.push.branch' "$trigger_spec")" \
            --substitutions="$(jq -r '.substitutions | to_entries | map("\(.key)=\(.value)") | join(",")' "$trigger_spec")"
        log_action "ensure_build_trigger" "created" "\"trigger\": \"$trigger_name\""
    fi
}

# Ensure Cloud Scheduler job exists
ensure_scheduler_job() {
    local job_name="$1"
    local schedule="$2"
    local target_uri="$3"
    local http_method="${4:-POST}"
    local payload="${5:-{}}"
    
    if gcloud scheduler jobs describe "$job_name" --location="${_REGION:-australia-southeast1}" >/dev/null 2>&1; then
        log_action "ensure_scheduler_job" "exists" "\"job\": \"$job_name\""
    else
        gcloud scheduler jobs create http "$job_name" \
            --schedule="$schedule" \
            --uri="$target_uri" \
            --http-method="$http_method" \
            --headers="Content-Type=application/json" \
            --message-body="$payload" \
            --location="${_REGION:-australia-southeast1}"
        log_action "ensure_scheduler_job" "created" "\"job\": \"$job_name\", \"schedule\": \"$schedule\""
    fi
}

# Export functions for use in other scripts
export -f log_action ensure_api ensure_bucket ensure_artifact_repo ensure_sa ensure_iam_binding ensure_secret ensure_secret_random ensure_build_trigger ensure_scheduler_job
