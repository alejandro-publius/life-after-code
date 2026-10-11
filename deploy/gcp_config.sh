#!/usr/bin/env bash
# Read public identifiers as data. Never evaluate this file as shell code.

load_gcp_config() {
  local config_file="$1" line key value line_number=0
  local -A seen=()
  [[ -f "$config_file" ]] || return 0
  while IFS= read -r line || [[ -n "$line" ]]; do
    line_number=$((line_number + 1))
    line="${line%$'\r'}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    if [[ ! "$line" =~ ^([A-Z][A-Z0-9_]*)=(.*)$ ]]; then
      printf 'Invalid config syntax at line %s. Use NAME=value without quotes.\n' "$line_number" >&2
      return 1
    fi
    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"
    case "$key" in
      GCP_PROJECT_ID|GCP_PROJECT_NUMBER|GCP_REGION|GCP_WIF_POOL|GCP_WIF_PROVIDER|\
      GCP_SERVICE_ACCOUNT|GCP_BUILD_SERVICE_ACCOUNT|GCP_ARTIFACT_REPOSITORY|GCP_SOURCE_BUCKET|\
      GCP_SHOP_SERVICE|GCP_STAGING_SERVICE|GCP_RELAY_SERVICE|GCP_SHOP_SERVICE_ACCOUNT|\
      GCP_STAGING_SERVICE_ACCOUNT|GCP_RELAY_SERVICE_ACCOUNT|GITLAB_PROJECT_ID|GITLAB_PROJECT_PATH|\
      GITLAB_URL|FLOW_CONSUMER_ID|FLOW_SERVICE_ACCOUNT|DAWN_FLOW_CONSUMER_ID|WATCH_ISSUE_IID|\
      SHOP_URL|SHOP_STAGING_URL|RELAY_URL|SHOP_METRICS_URL|STATE_BUCKET|STATE_OBJECT|UNLEASH_URL) ;;
      *) printf 'Unsupported public config key at line %s: %s\n' "$line_number" "$key" >&2; return 1 ;;
    esac
    [[ ! ${seen[$key]+present} ]] || {
      printf 'Duplicate public config key at line %s: %s\n' "$line_number" "$key" >&2
      return 1
    }
    seen[$key]=true
    if [[ ! "$value" =~ ^[A-Za-z0-9_./@:-]*$ ]]; then
      printf 'Invalid public identifier at line %s: %s\n' "$line_number" "$key" >&2
      return 1
    fi
    # An exported CI value takes priority, even if it is intentionally empty.
    if [[ ! ${!key+present} ]]; then
      printf -v "$key" '%s' "$value"
      export "${key?}"
    fi
  done < "$config_file"
}
