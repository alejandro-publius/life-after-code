#!/usr/bin/env bash
# Sourced by setup and teardown after the ownership journal is ready.
# Request values stay in Python memory, not in shell arguments or state backups.

setup_service_ops() {
  export LAC_OPS_STATE_FILE="$STATE_FILE" LAC_OPS_OWNER_DESCRIPTION="$OWNER_DESCRIPTION"
  export LAC_OPS_SOURCE_BUCKET="$GCP_SOURCE_BUCKET"
  export GCP_RELAY_KEY_SECRET="${GCP_RELAY_KEY_SECRET:-relay-key}"
  export RELAY_URL
  python3 "${LAC_OPS_HELPER:-$DEPLOY_DIRECTORY/monitoring.py}" setup
  backup_state
}

teardown_service_ops() {
  export LAC_OPS_STATE_FILE="$STATE_FILE" LAC_OPS_OWNER_DESCRIPTION="$OWNER_DESCRIPTION"
  export LAC_OPS_SOURCE_BUCKET="$GCP_SOURCE_BUCKET"
  python3 "${LAC_OPS_HELPER:-$DEPLOY_DIRECTORY/monitoring.py}" teardown
  backup_state
}
