#!/usr/bin/env bash
# Shared setup helpers. No account keys are read or created here.

set -euo pipefail

DEPLOY_DIRECTORY="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
STATE_HELPER="$DEPLOY_DIRECTORY/bootstrap_state.py"
STATE_FILE="${LAC_STATE_FILE:-$DEPLOY_DIRECTORY/.life-after-code-bootstrap.json}"
WORK_DIRECTORY="$(mktemp -d)"
trap 'rm -rf -- "$WORK_DIRECTORY"' EXIT
RESOURCE_JSON="$WORK_DIRECTORY/resource.json"

fail() {
  printf '%s\n' "$*" >&2
  exit 1
}

require_tools() {
  command -v gcloud >/dev/null || fail 'Open Cloud Shell first. The gcloud command is required.'
  command -v python3 >/dev/null || fail 'Python 3 is required.'
}

required() {
  [[ -n "${!1:-}" ]] || fail "Set $1 first."
}

configure_names() {
  required GCP_PROJECT_ID
  required GITLAB_PROJECT_ID
  required GITLAB_PROJECT_PATH
  export CLOUDSDK_CORE_PROJECT="$GCP_PROJECT_ID"
  [[ "$GCP_PROJECT_ID" =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ ]] || fail 'Invalid Google Cloud project ID.'
  [[ "$GITLAB_PROJECT_ID" =~ ^[0-9]{1,15}$ ]] || fail 'GitLab project ID must be numeric and at most 15 digits.'
  [[ "$GITLAB_PROJECT_PATH" =~ ^[A-Za-z0-9_.-]+(/[A-Za-z0-9_.-]+)+$ ]] || fail 'GitLab path must be namespace/project, without a URL.'
  export GCP_REGION="${GCP_REGION:-us-central1}"
  [[ "$GCP_REGION" =~ ^[a-z]+-[a-z]+[0-9]$ ]] || fail 'Invalid Google Cloud region.'
  export GCP_WIF_POOL="lac-${GITLAB_PROJECT_ID}-pool"
  export GCP_WIF_PROVIDER='gitlab'
  export GCP_RUN_SERVICE="lac-${GITLAB_PROJECT_ID}"
  export GCP_ARTIFACT_REPOSITORY="lac-${GITLAB_PROJECT_ID}"
  export GCP_SOURCE_BUCKET="${GCP_PROJECT_ID}-lac-${GITLAB_PROJECT_ID}-source"
  export GCP_SERVICE_ACCOUNT="lac-${GITLAB_PROJECT_ID}-deploy@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
  export GCP_BUILD_SERVICE_ACCOUNT="lac-${GITLAB_PROJECT_ID}-build@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
  export GCP_RUNTIME_SERVICE_ACCOUNT="lac-${GITLAB_PROJECT_ID}-runtime@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
  export OWNER_DESCRIPTION="Life After Code bootstrap: GitLab $GITLAB_PROJECT_PATH, project $GITLAB_PROJECT_ID."
  export BUDGET_DISPLAY="LAC $GITLAB_PROJECT_ID $GCP_PROJECT_ID"
  [[ "${#OWNER_DESCRIPTION}" -le 256 ]] || fail 'GitLab path is too long for the ownership description.'
}

# A missing resource is recoverable. Authentication and permission failures are not.
describe_optional() {
  local error_file="$WORK_DIRECTORY/describe-error.txt"
  if "$@" >"$RESOURCE_JSON" 2>"$error_file"; then
    return 0
  fi
  if python3 - "$error_file" <<'PY'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1]).read_text()
denied = re.search(r'PERMISSION_DENIED|UNAUTHENTICATED|permission|not authorized|disabled', text, re.I)
missing = re.search(r'NOT_FOUND|not found|does not exist|was not found|status.?404', text, re.I)
raise SystemExit(0 if missing and not denied else 1)
PY
  then
    return 1
  fi
  cat "$error_file" >&2
  fail 'A cloud command failed. Setup or teardown stopped without treating it as a missing resource.'
}

assert_owned() {
  python3 "$STATE_HELPER" assert "$RESOURCE_JSON" "$1" "$2"
}

state() {
  python3 "$STATE_HELPER" "$1" "$STATE_FILE" "${@:2}"
}

backup_state() {
  if [[ "${BUCKET_READY:-false}" == true ]]; then
    gcloud storage cp "$STATE_FILE" "gs://$GCP_SOURCE_BUCKET/bootstrap/state.json" \
      --project="$GCP_PROJECT_ID" --quiet >/dev/null
  fi
}

journal_resource() {
  state append resources "$1"
  backup_state
}

restore_state() {
  if [[ -f "$STATE_FILE" ]]; then
    state verify
    return 0
  fi
  if describe_optional gcloud storage buckets describe "gs://$GCP_SOURCE_BUCKET" \
      --project="$GCP_PROJECT_ID" --format=json; then
    assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
    if describe_optional gcloud storage objects describe "gs://$GCP_SOURCE_BUCKET/bootstrap/state.json" \
        --project="$GCP_PROJECT_ID" --format=json; then
      gcloud storage cp "gs://$GCP_SOURCE_BUCKET/bootstrap/state.json" "$STATE_FILE" \
        --project="$GCP_PROJECT_ID" --quiet >/dev/null
      state verify
      BUCKET_READY=true
      return 0
    fi
    fail 'An owned bucket exists without ownership metadata. Restore the local metadata before continuing.'
  fi
  return 1
}

project_binding() {
  journal_resource "project-binding:$1:$2"
  gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:$1" --role="$2" --condition=None --quiet >/dev/null
}

print_variables() {
  local key
  for key in GCP_PROJECT_ID GCP_PROJECT_NUMBER GCP_REGION GCP_WIF_POOL GCP_WIF_PROVIDER \
      GCP_SERVICE_ACCOUNT GCP_BUILD_SERVICE_ACCOUNT GCP_RUNTIME_SERVICE_ACCOUNT \
      GCP_ARTIFACT_REPOSITORY GCP_SOURCE_BUCKET GCP_RUN_SERVICE GITLAB_PROJECT_ID GITLAB_PROJECT_PATH; do
    printf '%s=%s\n' "$key" "${!key}"
  done
}
