#!/bin/bash
# State Writer Script
# Writes deployment state to GCS with support for extra fragments

set -euo pipefail

# Default values
PROJECT_ID="${_PROJECT_ID:-virtual-stratum-473511-u5}"
REGION="${_REGION:-australia-southeast1}"
STATE_BUCKET="${STATE_BUCKET:-anzx-deploy-state}"
BUILD_ID="${BUILD_ID:-${BUILD_ID:-manual-$(date +%Y%m%d-%H%M%S)}}"
SHORT_SHA="${SHORT_SHA:-$(echo $BUILD_ID | cut -c1-7)}"

# Function to write state with optional extra fragments
write_state() {
    local state_file="$1"
    local extra_fragments="${2:-}"
    
    # Create base state
    local base_state=$(cat << EOF
{
  "deployment": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "build_id": "$BUILD_ID",
    "short_sha": "$SHORT_SHA",
    "project_id": "$PROJECT_ID",
    "region": "$REGION",
    "state_bucket": "$STATE_BUCKET"
  }
}
EOF
)
    
    # Merge extra fragments if provided
    if [[ -n "$extra_fragments" ]]; then
        # Parse extra fragments and merge into base state
        local merged_state=$(echo "$base_state" | jq --argjson extra "$extra_fragments" '. * $extra')
        echo "$merged_state" > "/tmp/$state_file"
    else
        echo "$base_state" > "/tmp/$state_file"
    fi
    
    # Upload to GCS
    gsutil cp "/tmp/$state_file" "gs://$STATE_BUCKET/state/$state_file"
    
    echo "{\"action\": \"write_state\", \"status\": \"success\", \"file\": \"$state_file\", \"bucket\": \"$STATE_BUCKET\"}"
}

# Function to append to existing state
append_state() {
    local state_file="$1"
    local fragment="$2"
    
    # Download existing state or create new
    if gsutil cp "gs://$STATE_BUCKET/state/$state_file" "/tmp/$state_file" 2>/dev/null; then
        # Merge with existing state
        local merged_state=$(cat "/tmp/$state_file" | jq --argjson fragment "$fragment" '. * $fragment')
        echo "$merged_state" > "/tmp/$state_file"
    else
        # Create new state with fragment
        echo "$fragment" > "/tmp/$state_file"
    fi
    
    # Upload back to GCS
    gsutil cp "/tmp/$state_file" "gs://$STATE_BUCKET/state/$state_file"
    
    echo "{\"action\": \"append_state\", \"status\": \"success\", \"file\": \"$state_file\"}"
}

# Main execution
case "${1:-write}" in
    "write")
        write_state "${2:-deploy-${SHORT_SHA}.json}" "${3:-}"
        ;;
    "append")
        append_state "${2:-deploy-${SHORT_SHA}.json}" "${3:-{}}"
        ;;
    *)
        echo "Usage: $0 [write|append] <state_file> [fragment]"
        echo "  write: Create new state file with optional fragment"
        echo "  append: Append fragment to existing state file"
        exit 1
        ;;
esac
