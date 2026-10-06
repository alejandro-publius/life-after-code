#!/usr/bin/env bash
# Run by Alex in Cloud Shell. This creates no service account keys.

set -euo pipefail
# shellcheck source=deploy/lib.sh
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib.sh"

require_tools
configure_names
required GITLAB_NAMESPACE_ID
[[ "$GITLAB_NAMESPACE_ID" =~ ^[0-9]+$ ]] || fail 'GitLab namespace ID must be numeric.'
export GITLAB_DEFAULT_BRANCH="${GITLAB_DEFAULT_BRANCH:-main}"
[[ "$GITLAB_DEFAULT_BRANCH" =~ ^[A-Za-z0-9_./-]+$ ]] || fail 'Invalid default branch name.'
[[ "${GCP_DEDICATED_PROJECT:-false}" == true ]] || fail 'Set GCP_DEDICATED_PROJECT=true only for a separate project created for this entry.'

gcloud projects describe "$GCP_PROJECT_ID" --format=json >"$RESOURCE_JSON"
export GCP_PROJECT_NUMBER
GCP_PROJECT_NUMBER="$(python3 "$STATE_HELPER" get "$RESOURCE_JSON" projectNumber)"
existing_owner="$(python3 - "$RESOURCE_JSON" <<'PY'
import json, sys
print(json.load(open(sys.argv[1])).get('labels', {}).get('lac-owner', ''))
PY
)"
[[ -z "$existing_owner" || "$existing_owner" == "$GITLAB_PROJECT_ID" ]] || fail 'The Google Cloud project has a different bootstrap owner.'

export GCP_BILLING_ACCOUNT_ID="${GCP_BILLING_ACCOUNT_ID:-pending}"
if [[ -f "$STATE_FILE" || -n "$existing_owner" ]]; then
  restore_state || fail 'Owned setup metadata cannot be restored. No unknown resources will be adopted.'
  for key in GCP_REGION GITLAB_NAMESPACE_ID GITLAB_DEFAULT_BRANCH; do
    [[ "${!key}" == "$(state get "config.$key")" ]] || fail "Saved $key differs. Use the original value or tear down first."
  done
else
  python3 "$STATE_HELPER" new "$STATE_FILE"
fi
state set complete false
state set teardown_complete false
state set teardown_resources_removed false
backup_state

if [[ -z "$existing_owner" ]]; then
  state set project_label_added true
  backup_state
  gcloud projects update "$GCP_PROJECT_ID" --update-labels="lac-owner=$GITLAB_PROJECT_ID" --quiet >/dev/null
fi

gcloud services list --enabled --project="$GCP_PROJECT_ID" --format=json >"$WORK_DIRECTORY/apis.json"
apis=(serviceusage.googleapis.com cloudresourcemanager.googleapis.com iam.googleapis.com \
  iamcredentials.googleapis.com sts.googleapis.com run.googleapis.com artifactregistry.googleapis.com \
  cloudbuild.googleapis.com storage.googleapis.com logging.googleapis.com cloudbilling.googleapis.com billingbudgets.googleapis.com)
for api in "${apis[@]}"; do
  if ! python3 - "$WORK_DIRECTORY/apis.json" "$api" <<'PY'
import json, sys
services = json.load(open(sys.argv[1]))
raise SystemExit(0 if any(s.get('config', {}).get('name') == sys.argv[2] for s in services) else 1)
PY
  then
    state append enabled_apis "$api"
    backup_state
    gcloud services enable "$api" --project="$GCP_PROJECT_ID" --quiet >/dev/null
  fi
done
# API activation can also enable dependencies. Keep those in the same ownership journal.
gcloud services list --enabled --project="$GCP_PROJECT_ID" --format=json >"$WORK_DIRECTORY/apis-after.json"
python3 - "$WORK_DIRECTORY/apis.json" "$WORK_DIRECTORY/apis-after.json" >"$WORK_DIRECTORY/new-apis.txt" <<'PY'
import json, sys
before = {item['config']['name'] for item in json.load(open(sys.argv[1]))}
after = {item['config']['name'] for item in json.load(open(sys.argv[2]))}
for name in sorted(after - before):
    print(name)
PY
while IFS= read -r api; do
  state append enabled_apis "$api"
done <"$WORK_DIRECTORY/new-apis.txt"
backup_state
gcloud billing projects describe "$GCP_PROJECT_ID" --format=json >"$WORK_DIRECTORY/billing.json"
export GCP_BILLING_ACCOUNT_ID
GCP_BILLING_ACCOUNT_ID="$(python3 - "$WORK_DIRECTORY/billing.json" <<'PY'
import json, sys
value = json.load(open(sys.argv[1]))
if not value.get('billingEnabled') or not value.get('billingAccountName'):
    raise SystemExit('Link an active billing account to this dedicated project first.')
print(value['billingAccountName'].split('/')[-1])
PY
)"
saved_billing="$(state get config.GCP_BILLING_ACCOUNT_ID)"
[[ "$saved_billing" == pending || "$saved_billing" == "$GCP_BILLING_ACCOUNT_ID" ]] || fail 'The saved billing account differs. Use the original account or tear down first.'
state config GCP_BILLING_ACCOUNT_ID "$GCP_BILLING_ACCOUNT_ID"
backup_state

# Check billing permissions now. A budget failure must not become a silent skip.
gcloud billing budgets list --billing-account="$GCP_BILLING_ACCOUNT_ID" \
  --format=json >"$WORK_DIRECTORY/budgets.json"
budget_name="$(python3 "$STATE_HELPER" budget "$WORK_DIRECTORY/budgets.json" \
  "$GCP_PROJECT_ID" "$GCP_PROJECT_NUMBER" "$BUDGET_DISPLAY")"
saved_budget="$(state get budget_name)"
if [[ -n "$budget_name" && "$saved_budget" != "$budget_name" ]]; then
  if [[ "$saved_budget" != null ]] || ! state contains resources budget; then
    fail 'A matching budget already exists without saved ownership. Choose a separate dedicated project.'
  fi
  budget_json="$(python3 - "$budget_name" <<'PY'
import json, sys
print(json.dumps(sys.argv[1]))
PY
)"
  state set budget_name "$budget_json"
  backup_state
fi

for api in cloudbuild.googleapis.com run.googleapis.com; do
  gcloud beta services identity create --service="$api" --project="$GCP_PROJECT_ID" --quiet >/dev/null
done

if describe_optional gcloud storage buckets describe "gs://$GCP_SOURCE_BUCKET" \
    --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
  state contains resources source-bucket || fail 'The bucket marker matches but the saved creation journal does not. Restore its original metadata.'
else
  journal_resource source-bucket
  gcloud storage buckets create "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" \
    --location="$GCP_REGION" --uniform-bucket-level-access --public-access-prevention \
    --soft-delete-duration=0 --quiet >/dev/null
  gcloud storage buckets update "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" \
    --update-labels="lac-owner=$GITLAB_PROJECT_ID" --quiet >/dev/null
fi
export BUCKET_READY=true
backup_state
cat >"$WORK_DIRECTORY/lifecycle.json" <<'JSON'
{"rule":[{"action":{"type":"Delete"},"condition":{"age":1,"matchesPrefix":["source/"]}}]}
JSON
gcloud storage buckets update "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" \
  --uniform-bucket-level-access --public-access-prevention --soft-delete-duration=0 \
  --lifecycle-file="$WORK_DIRECTORY/lifecycle.json" --quiet >/dev/null

for kind in deploy build runtime; do
  account_id="lac-${GITLAB_PROJECT_ID}-${kind}"
  account_email="$account_id@$GCP_PROJECT_ID.iam.gserviceaccount.com"
  if describe_optional gcloud iam service-accounts describe "$account_email" \
      --project="$GCP_PROJECT_ID" --format=json; then
    assert_owned description "$OWNER_DESCRIPTION"
  else
    journal_resource "sa-$kind"
    gcloud iam service-accounts create "$account_id" --project="$GCP_PROJECT_ID" \
      --display-name="LAC $kind $GITLAB_PROJECT_ID" --description="$OWNER_DESCRIPTION" --quiet >/dev/null
  fi
done

if describe_optional gcloud iam workload-identity-pools describe "$GCP_WIF_POOL" \
    --location=global --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned description "$OWNER_DESCRIPTION"
  if python3 "$STATE_HELPER" equals "$RESOURCE_JSON" state '"DELETED"'; then
    gcloud iam workload-identity-pools undelete "$GCP_WIF_POOL" --location=global \
      --project="$GCP_PROJECT_ID" --quiet >/dev/null
  fi
else
  journal_resource wif-pool
  gcloud iam workload-identity-pools create "$GCP_WIF_POOL" --location=global \
    --project="$GCP_PROJECT_ID" --display-name="LAC $GITLAB_PROJECT_ID" \
    --description="$OWNER_DESCRIPTION" --quiet >/dev/null
fi
mapping='google.subject=assertion.sub,attribute.project_id=assertion.project_id,attribute.project_path=assertion.project_path,attribute.namespace_id=assertion.namespace_id,attribute.ref=assertion.ref,attribute.ref_type=assertion.ref_type,attribute.ref_protected=assertion.ref_protected'
condition="assertion.project_path=='$GITLAB_PROJECT_PATH' && assertion.project_id=='$GITLAB_PROJECT_ID' && assertion.namespace_id=='$GITLAB_NAMESPACE_ID' && assertion.ref_type=='branch' && assertion.ref=='$GITLAB_DEFAULT_BRANCH' && assertion.ref_protected=='true'"
if describe_optional gcloud iam workload-identity-pools providers describe "$GCP_WIF_PROVIDER" \
    --workload-identity-pool="$GCP_WIF_POOL" --location=global --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned description "$OWNER_DESCRIPTION"
  if python3 "$STATE_HELPER" equals "$RESOURCE_JSON" state '"DELETED"'; then
    gcloud iam workload-identity-pools providers undelete "$GCP_WIF_PROVIDER" \
      --workload-identity-pool="$GCP_WIF_POOL" --location=global --project="$GCP_PROJECT_ID" --quiet >/dev/null
  fi
  gcloud iam workload-identity-pools providers update-oidc "$GCP_WIF_PROVIDER" \
    --workload-identity-pool="$GCP_WIF_POOL" --location=global --project="$GCP_PROJECT_ID" \
    --issuer-uri=https://gitlab.com --allowed-audiences=https://gitlab.com \
    --attribute-mapping="$mapping" --attribute-condition="$condition" --quiet >/dev/null
else
  journal_resource wif-provider
  gcloud iam workload-identity-pools providers create-oidc "$GCP_WIF_PROVIDER" \
    --workload-identity-pool="$GCP_WIF_POOL" --location=global --project="$GCP_PROJECT_ID" \
    --issuer-uri=https://gitlab.com --allowed-audiences=https://gitlab.com \
    --display-name="LAC GitLab $GITLAB_PROJECT_ID" --description="$OWNER_DESCRIPTION" \
    --attribute-mapping="$mapping" --attribute-condition="$condition" --quiet >/dev/null
fi
principal="principalSet://iam.googleapis.com/projects/$GCP_PROJECT_NUMBER/locations/global/workloadIdentityPools/$GCP_WIF_POOL/attribute.project_id/$GITLAB_PROJECT_ID"
gcloud iam service-accounts add-iam-policy-binding "$GCP_SERVICE_ACCOUNT" --project="$GCP_PROJECT_ID" \
  --member="$principal" --role=roles/iam.workloadIdentityUser --condition=None --quiet >/dev/null

if describe_optional gcloud artifacts repositories describe "$GCP_ARTIFACT_REPOSITORY" \
    --location="$GCP_REGION" --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned labels.lac-owner "$GITLAB_PROJECT_ID"
  assert_owned format DOCKER
else
  journal_resource artifact-repository
  gcloud artifacts repositories create "$GCP_ARTIFACT_REPOSITORY" --location="$GCP_REGION" \
    --project="$GCP_PROJECT_ID" --repository-format=docker --description="$OWNER_DESCRIPTION" \
    --labels="lac-owner=$GITLAB_PROJECT_ID" --quiet >/dev/null
fi
for binding in "$GCP_SERVICE_ACCOUNT roles/artifactregistry.reader" "$GCP_BUILD_SERVICE_ACCOUNT roles/artifactregistry.writer"; do
  read -r account role <<<"$binding"
  gcloud artifacts repositories add-iam-policy-binding "$GCP_ARTIFACT_REPOSITORY" \
    --location="$GCP_REGION" --project="$GCP_PROJECT_ID" --member="serviceAccount:$account" \
    --role="$role" --condition=None --quiet >/dev/null
done
gcloud storage buckets add-iam-policy-binding "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" \
  --member="serviceAccount:$GCP_SERVICE_ACCOUNT" --role=roles/storage.objectUser --quiet >/dev/null
gcloud storage buckets add-iam-policy-binding "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" \
  --member="serviceAccount:$GCP_SERVICE_ACCOUNT" --role=roles/storage.legacyBucketReader --quiet >/dev/null
gcloud storage buckets add-iam-policy-binding "gs://$GCP_SOURCE_BUCKET" --project="$GCP_PROJECT_ID" \
  --member="serviceAccount:$GCP_BUILD_SERVICE_ACCOUNT" --role=roles/storage.objectViewer --quiet >/dev/null
project_binding "$GCP_SERVICE_ACCOUNT" roles/cloudbuild.builds.editor
project_binding "$GCP_SERVICE_ACCOUNT" roles/serviceusage.serviceUsageConsumer
project_binding "$GCP_BUILD_SERVICE_ACCOUNT" roles/logging.logWriter
for account in "$GCP_BUILD_SERVICE_ACCOUNT" "$GCP_RUNTIME_SERVICE_ACCOUNT"; do
  gcloud iam service-accounts add-iam-policy-binding "$account" --project="$GCP_PROJECT_ID" \
    --member="serviceAccount:$GCP_SERVICE_ACCOUNT" --role=roles/iam.serviceAccountUser \
    --condition=None --quiet >/dev/null
done

if describe_optional gcloud run services describe "$GCP_RUN_SERVICE" \
    --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format=json; then
  assert_owned metadata.labels.lac-owner "$GITLAB_PROJECT_ID"
else
  journal_resource run-service
  gcloud run deploy "$GCP_RUN_SERVICE" --project="$GCP_PROJECT_ID" --region="$GCP_REGION" \
    --image=us-docker.pkg.dev/cloudrun/container/hello \
    --service-account="$GCP_RUNTIME_SERVICE_ACCOUNT" --labels="lac-owner=$GITLAB_PROJECT_ID" \
    --no-invoker-iam-check --min=0 --max=1 --min-instances=0 --max-instances=1 \
    --cpu=1 --memory=256Mi --concurrency=20 --timeout=30 \
    --cpu-throttling --no-cpu-boost --quiet >/dev/null
fi
gcloud run services add-iam-policy-binding "$GCP_RUN_SERVICE" --project="$GCP_PROJECT_ID" \
  --region="$GCP_REGION" --member="serviceAccount:$GCP_SERVICE_ACCOUNT" \
  --role=roles/run.developer --condition=None --quiet >/dev/null

if [[ -z "$budget_name" ]]; then
  journal_resource budget
  gcloud billing budgets create --billing-account="$GCP_BILLING_ACCOUNT_ID" \
    --display-name="$BUDGET_DISPLAY" --budget-amount=5USD --calendar-period=month \
    --filter-projects="projects/$GCP_PROJECT_ID" --threshold-rule=percent=0.5 \
    --threshold-rule=percent=0.9 --threshold-rule=percent=1.0 --format=json >"$RESOURCE_JSON"
  budget_name="$(python3 "$STATE_HELPER" get "$RESOURCE_JSON" name)"
  budget_json="$(python3 - "$budget_name" <<'PY'
import json, sys
print(json.dumps(sys.argv[1]))
PY
)"
  state set budget_name "$budget_json"
  backup_state
else
  gcloud billing budgets update "$budget_name" --budget-amount=5USD --calendar-period=month \
    --filter-projects="projects/$GCP_PROJECT_ID" --clear-threshold-rules \
    --add-threshold-rule=percent=0.5 --add-threshold-rule=percent=0.9 \
    --add-threshold-rule=percent=1.0 --quiet >/dev/null
fi
state set complete true
state set teardown_complete false
state set teardown_resources_removed false
backup_state
printf '%s\n' 'Setup complete. The budget sends alerts; it does not cap spending.' \
  'Protect the default branch in GitLab. Paste these values into protected CI/CD variables:'
print_variables
