#!/usr/bin/env bash
# Delete owned bootstrap resources. Never delete the parent project.

set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

require_tools
configure_names
[[ "$#" == 2 && "$1" == --confirm-project && "$2" == "$GCP_PROJECT_ID" ]] || \
  fail 'Usage: bash deploy/teardown_gcp.sh --confirm-project YOUR_EXACT_PROJECT_ID'
if ! restore_state; then
  fail 'Ownership metadata is missing. No resources were deleted. Restore the local file or the owned bucket backup.'
fi
if python3 - "$STATE_FILE" <<'PY'
import json, sys
raise SystemExit(0 if json.load(open(sys.argv[1])).get('teardown_complete') else 1)
PY
then
  printf '%s\n' 'This saved setup was already removed.'
  exit 0
fi

for key in GCP_PROJECT_NUMBER GCP_REGION GCP_BILLING_ACCOUNT_ID GITLAB_NAMESPACE_ID GITLAB_DEFAULT_BRANCH; do
  printf -v "$key" '%s' "$(state get "config.$key")"
  export "${key?}"
done
if ! state equals teardown_resources_removed true; then
gcloud projects describe "$GCP_PROJECT_ID" --format=json >"$RESOURCE_JSON"
assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"

owns_resource() {
  python3 - "$STATE_FILE" "$1" <<'PY'
import json, sys
raise SystemExit(0 if sys.argv[2] in json.load(open(sys.argv[1]))['resources'] else 1)
PY
}

# Builds use only the dedicated builder identity. Do not cancel anyone else's builds.
if owns_resource sa-build; then
  gcloud builds list --project="$GCP_PROJECT_ID" --region="$GCP_REGION" \
    --format=json >"$WORK_DIRECTORY/builds.json"
  python3 - "$WORK_DIRECTORY/builds.json" "$GCP_BUILD_SERVICE_ACCOUNT" >"$WORK_DIRECTORY/build-ids.txt" <<'PY'
import json, sys
for build in json.load(open(sys.argv[1])):
    account = build.get('serviceAccount', '').split('/')[-1]
    if account == sys.argv[2] and build.get('status') in ('PENDING', 'QUEUED', 'WORKING'):
        print(build['id'])
PY
  while IFS= read -r build_id; do
    [[ -z "$build_id" ]] || gcloud builds cancel "$build_id" --project="$GCP_PROJECT_ID" \
      --region="$GCP_REGION" --quiet >/dev/null
  done <"$WORK_DIRECTORY/build-ids.txt"
fi

if owns_resource run-service && describe_optional gcloud run services describe "$GCP_RUN_SERVICE" \
    --project="$GCP_PROJECT_ID" --region="$GCP_REGION" --format=json; then
  assert_owned metadata.labels.lac-owner "$GITLAB_PROJECT_ID"
  gcloud run services delete "$GCP_RUN_SERVICE" --project="$GCP_PROJECT_ID" \
    --region="$GCP_REGION" --quiet >/dev/null
fi
if owns_resource artifact-repository && describe_optional gcloud artifacts repositories describe "$GCP_ARTIFACT_REPOSITORY" \
    --project="$GCP_PROJECT_ID" --location="$GCP_REGION" --format=json; then
  assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
  gcloud artifacts repositories delete "$GCP_ARTIFACT_REPOSITORY" --project="$GCP_PROJECT_ID" \
    --location="$GCP_REGION" --quiet >/dev/null
fi

budget_name="$(state get budget_name)"
if owns_resource budget; then
  # Recover the create response if setup was interrupted before writing the budget ID.
  gcloud billing budgets list --billing-account="$GCP_BILLING_ACCOUNT_ID" \
    --format=json >"$WORK_DIRECTORY/budgets.json"
  discovered_budget="$(python3 "$STATE_HELPER" budget "$WORK_DIRECTORY/budgets.json" \
    "$GCP_PROJECT_ID" "$GCP_PROJECT_NUMBER" "$BUDGET_DISPLAY")"
  if [[ -n "$discovered_budget" ]]; then
    [[ "$budget_name" == null || "$budget_name" == "$discovered_budget" ]] || fail 'The saved budget ID differs from the owned budget.'
    gcloud billing budgets delete "$discovered_budget" --quiet >/dev/null
  fi
fi

if owns_resource wif-provider && describe_optional gcloud iam workload-identity-pools providers describe "$GCP_WIF_PROVIDER" \
    --workload-identity-pool="$GCP_WIF_POOL" --location=global --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned description "$OWNER_DESCRIPTION"
  if ! python3 "$STATE_HELPER" equals "$RESOURCE_JSON" state '"DELETED"'; then
    gcloud iam workload-identity-pools providers delete "$GCP_WIF_PROVIDER" \
      --workload-identity-pool="$GCP_WIF_POOL" --location=global --project="$GCP_PROJECT_ID" --quiet >/dev/null
  fi
fi
if owns_resource wif-pool && describe_optional gcloud iam workload-identity-pools describe "$GCP_WIF_POOL" \
    --location=global --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned description "$OWNER_DESCRIPTION"
  if ! python3 "$STATE_HELPER" equals "$RESOURCE_JSON" state '"DELETED"'; then
    gcloud iam workload-identity-pools delete "$GCP_WIF_POOL" \
      --location=global --project="$GCP_PROJECT_ID" --quiet >/dev/null
  fi
fi

# Delete only the three exact project bindings added by this bootstrap.
gcloud projects get-iam-policy "$GCP_PROJECT_ID" --format=json >"$WORK_DIRECTORY/policy.json"
for binding in "$GCP_SERVICE_ACCOUNT roles/cloudbuild.builds.editor" \
    "$GCP_SERVICE_ACCOUNT roles/serviceusage.serviceUsageConsumer" \
    "$GCP_BUILD_SERVICE_ACCOUNT roles/logging.logWriter"; do
  read -r account role <<<"$binding"
  owns_resource "project-binding:$account:$role" || continue
  if python3 - "$WORK_DIRECTORY/policy.json" "$account" "$role" <<'PY'
import json, sys
bindings = json.load(open(sys.argv[1])).get('bindings', [])
present = any(b.get('role') == sys.argv[3] and not b.get('condition')
              and 'serviceAccount:' + sys.argv[2] in b.get('members', []) for b in bindings)
raise SystemExit(0 if present else 1)
PY
  then
    gcloud projects remove-iam-policy-binding "$GCP_PROJECT_ID" \
      --member="serviceAccount:$account" --role="$role" --condition=None --quiet >/dev/null
  fi
done
for kind in deploy build runtime; do
  if owns_resource "sa-$kind"; then
    account_email="lac-${GITLAB_PROJECT_ID}-${kind}@$GCP_PROJECT_ID.iam.gserviceaccount.com"
    if describe_optional gcloud iam service-accounts describe "$account_email" \
        --project="$GCP_PROJECT_ID" --format=json; then
      assert_owned description "$OWNER_DESCRIPTION"
      gcloud iam service-accounts delete "$account_email" --project="$GCP_PROJECT_ID" --quiet >/dev/null
    fi
  fi
done
if owns_resource source-bucket && describe_optional gcloud storage buckets describe "gs://$GCP_SOURCE_BUCKET" \
    --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
  # This bucket is disposable source and ownership metadata, never app data.
  gcloud storage buckets update "gs://$GCP_SOURCE_BUCKET" --soft-delete-duration=0 \
    --project="$GCP_PROJECT_ID" --quiet >/dev/null
  gcloud storage rm --recursive "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" --quiet >/dev/null
fi
export BUCKET_READY=false
if [[ "$(state get project_label_added)" == true ]]; then
  gcloud alpha projects update "$GCP_PROJECT_ID" --remove-labels=lac-owner --quiet >/dev/null
fi
state set teardown_resources_removed true
fi

# Disable only APIs first enabled by this setup. Do not use force on dependencies.
gcloud services list --enabled --project="$GCP_PROJECT_ID" --format=json >"$WORK_DIRECTORY/enabled-now.json"
python3 - "$STATE_FILE" "$WORK_DIRECTORY/enabled-now.json" >"$WORK_DIRECTORY/disable-apis.txt" <<'PY'
import json, sys
state = json.load(open(sys.argv[1]))
enabled = {item['config']['name'] for item in json.load(open(sys.argv[2]))}
for name in reversed(state['enabled_apis']):
    if name in enabled:
        print(name)
PY
mapfile -t disable_apis <"$WORK_DIRECTORY/disable-apis.txt"
if [[ "${#disable_apis[@]}" -gt 0 ]]; then
  gcloud services disable "${disable_apis[@]}" --project="$GCP_PROJECT_ID" --quiet >/dev/null
fi
state set complete false
state set teardown_complete true
printf '%s\n' 'Owned resources removed. The parent project and its billing link remain.' \
  'For a complete stop, unlink billing or shut down the dedicated project in Google Cloud.'
