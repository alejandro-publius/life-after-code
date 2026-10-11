#!/usr/bin/env bash
# Secret values stay in a private temporary file, never in a cloud command line.

setup_service_secrets() {
  local secret_id secret_file account has_version
  local -a accounts=()
  # Even a caller using bash -x must not trace a secret read or a generated topic.
  set +x
  for secret_id in gitlab-token unleash-instance-id relay-key demo-key ntfy-url; do
    if describe_optional gcloud secrets describe "$secret_id" --project="$GCP_PROJECT_ID" --format=json; then
      assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
      owns_resource "secret-$secret_id" || fail 'The secret lacks a saved creation journal.'
    else
      journal_resource "secret-$secret_id"
      gcloud secrets create "$secret_id" --project="$GCP_PROJECT_ID" --replication-policy=automatic \
        --labels="lac-owner=$GITLAB_PROJECT_ID" --quiet >/dev/null
    fi
    gcloud secrets versions list "$secret_id" --project="$GCP_PROJECT_ID" \
      --format=json >"$WORK_DIRECTORY/versions.json"
    has_version="$(python3 - "$WORK_DIRECTORY/versions.json" <<'PY'
import json, sys
versions = json.load(open(sys.argv[1]))
if versions:
    latest = max(versions, key=lambda v: int(v['name'].rsplit('/', 1)[-1]))
    if latest.get('state') != 'ENABLED':
        raise SystemExit('The latest secret version is disabled or destroyed. Restore it explicitly; setup will not rotate a key.')
print('true' if versions else 'false')
PY
)"
    if [[ "$has_version" != true ]]; then
      secret_file="$WORK_DIRECTORY/$secret_id.value"
      if [[ "$secret_id" == gitlab-token || "$secret_id" == unleash-instance-id ]]; then
        # /dev/tty allows this script to be pasted or piped without reading pasted commands as keys.
        [[ -r /dev/tty && -w /dev/tty ]] || fail 'Open interactive Cloud Shell to enter the two private values.'
        local entered_value=''
        export -n entered_value
        if ! IFS= read -r -s -p "Paste $secret_id (hidden), then press Enter: " entered_value </dev/tty; then
          fail 'The private value was not entered.'
        fi
        printf '\n' >/dev/tty
        [[ -n "$entered_value" ]] || fail 'An empty private value was refused.'
        printf '%s' "$entered_value" >"$secret_file"
        unset entered_value
      else
        python3 - "$secret_id" "$secret_file" <<'PY'
import pathlib, secrets, sys
value = secrets.token_urlsafe(32)
if sys.argv[1] == 'ntfy-url':
    value = 'https://ntfy.sh/' + value
pathlib.Path(sys.argv[2]).write_text(value)
PY
      fi
      chmod 600 "$secret_file"
      gcloud secrets versions add "$secret_id" --project="$GCP_PROJECT_ID" \
        --data-file="$secret_file" --quiet >/dev/null
      rm -f -- "$secret_file"
    fi
    case "$secret_id" in
      gitlab-token|relay-key|ntfy-url) accounts=("$GCP_RELAY_SERVICE_ACCOUNT") ;;
      unleash-instance-id) accounts=("$GCP_SHOP_SERVICE_ACCOUNT" "$GCP_STAGING_SERVICE_ACCOUNT") ;;
      demo-key) accounts=("$GCP_RELAY_SERVICE_ACCOUNT" "$GCP_SHOP_SERVICE_ACCOUNT" "$GCP_STAGING_SERVICE_ACCOUNT") ;;
    esac
    for account in "${accounts[@]}"; do
      gcloud secrets add-iam-policy-binding "$secret_id" --project="$GCP_PROJECT_ID" \
        --member="serviceAccount:$account" --role=roles/secretmanager.secretAccessor \
        --condition=None --quiet >/dev/null
    done
  done
}

teardown_service_secrets() {
  local secret_id
  for secret_id in gitlab-token unleash-instance-id relay-key demo-key ntfy-url; do
    if owns_resource "secret-$secret_id" && describe_optional gcloud secrets describe "$secret_id" \
        --project="$GCP_PROJECT_ID" --format=json; then
      assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
      gcloud secrets delete "$secret_id" --project="$GCP_PROJECT_ID" --quiet >/dev/null
    fi
  done
}
