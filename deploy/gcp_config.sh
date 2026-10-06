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
      GCP_SERVICE_ACCOUNT|GCP_BUILD_SERVICE_ACCOUNT|GCP_RUNTIME_SERVICE_ACCOUNT|\
      GCP_ARTIFACT_REPOSITORY|GCP_SOURCE_BUCKET|GCP_RUN_SERVICE|GITLAB_PROJECT_ID|GITLAB_PROJECT_PATH) ;;
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
