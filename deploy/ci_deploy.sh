#!/usr/bin/env bash
# Build and deploy one approved service without reading any runtime secret.
set +x
set -euo pipefail
umask 077
export CLOUDSDK_CORE_LOG_HTTP=false
export CLOUDSDK_CORE_VERBOSITY=warning

die() { printf '%s\n' "$*" >&2; exit 1; }
[[ ${CI_DEBUG_TRACE:-false} != true ]] || die 'Disable CI debug tracing before using credentials.'
# shellcheck source=deploy/gcp_config.sh
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/gcp_config.sh"
load_gcp_config "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/gcp.env"
target=${1:-${GCP_DEPLOY_TARGET:-shop}}
case "$target" in
  shop)
    service=${GCP_SHOP_SERVICE:-}; runtime_account=${GCP_SHOP_SERVICE_ACCOUNT:-}
    app_dir=shop; app_env=production; cpu_flag=--no-cpu-throttling; memory=512Mi; request_timeout=30s
    secret_refs='UNLEASH_INSTANCE_ID=unleash-instance-id:latest,DEMO_KEY=demo-key:latest' ;;
  shop-staging)
    service=${GCP_STAGING_SERVICE:-}; runtime_account=${GCP_STAGING_SERVICE_ACCOUNT:-}
    app_dir=shop; app_env=staging; cpu_flag=--no-cpu-throttling; memory=512Mi; request_timeout=30s
    secret_refs='UNLEASH_INSTANCE_ID=unleash-instance-id:latest,DEMO_KEY=demo-key:latest' ;;
  relay)
    service=${GCP_RELAY_SERVICE:-}; runtime_account=${GCP_RELAY_SERVICE_ACCOUNT:-}
    app_dir=relay; app_env=relay; cpu_flag=--cpu-throttling; memory=256Mi; request_timeout=60s
    secret_refs='GITLAB_TOKEN=gitlab-token:latest,RELAY_KEY=relay-key:latest,NTFY_URL=ntfy-url:latest,DEMO_KEY=demo-key:latest' ;;
  *) die 'Choose shop, shop-staging or relay.' ;;
esac
for name in GCP_PROJECT_ID GCP_PROJECT_NUMBER GCP_REGION GCP_WIF_POOL GCP_WIF_PROVIDER \
  GCP_SERVICE_ACCOUNT GCP_BUILD_SERVICE_ACCOUNT GCP_ARTIFACT_REPOSITORY GCP_SOURCE_BUCKET \
  GITLAB_PROJECT_ID GITLAB_PROJECT_PATH GITLAB_OIDC_TOKEN CI_COMMIT_SHA CI_COMMIT_SHORT_SHA \
  CI_PROJECT_ID CI_PROJECT_PATH CI_COMMIT_BRANCH CI_DEFAULT_BRANCH CI_COMMIT_REF_PROTECTED; do
  [[ -n ${!name:-} ]] || die "Missing required CI variable or public config: $name"
done
[[ $service == "$target" && -n $runtime_account ]] || die 'Service identity does not match the selected deployment.'
[[ $CI_PROJECT_ID == "$GITLAB_PROJECT_ID" && $CI_PROJECT_PATH == "$GITLAB_PROJECT_PATH" ]] || die 'The GitLab project does not match the configured trust.'
[[ $CI_COMMIT_BRANCH == "$CI_DEFAULT_BRANCH" && $CI_COMMIT_REF_PROTECTED == true ]] || die 'Only the protected default branch may deploy.'
[[ $CI_COMMIT_SHA =~ ^[0-9a-f]{40}$ && $CI_COMMIT_SHORT_SHA =~ ^[0-9a-f]{7,40}$ ]] || die 'Invalid candidate commit identity.'
[[ $GCP_PROJECT_ID =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ && $GCP_PROJECT_NUMBER =~ ^[0-9]+$ ]] || die 'Invalid Google project identity.'
for name in GCP_REGION GCP_WIF_POOL GCP_WIF_PROVIDER GCP_ARTIFACT_REPOSITORY GCP_SOURCE_BUCKET; do
  [[ ${!name} =~ ^[a-z0-9][a-z0-9-]+[a-z0-9]$ ]] || die "Invalid resource name: $name"
done
for account in "$GCP_SERVICE_ACCOUNT" "$GCP_BUILD_SERVICE_ACCOUNT" "$runtime_account"; do
  [[ $account == *@"$GCP_PROJECT_ID".iam.gserviceaccount.com ]] || die 'A service account belongs to a different Google project.'
done
export APP_ENV="$app_env"
if [[ $target == relay ]]; then
  for name in GITLAB_URL SHOP_METRICS_URL STATE_BUCKET STATE_OBJECT; do
    [[ -n ${!name:-} ]] || die "Missing relay public config: $name"
  done
  [[ $GITLAB_URL == https://gitlab.com ]] || die 'This deployment uses the GitLab.com project.'
  [[ $SHOP_METRICS_URL == https://*.run.app/metrics.json ]] || die 'The shop metrics URL must be its public Cloud Run /metrics.json.'
  [[ $STATE_BUCKET == "$GCP_PROJECT_ID-night-orders-state" && $STATE_OBJECT == night-orders/state.json ]] || die 'Relay state must use the owned Night Orders bucket and object.'
  for name in FLOW_CONSUMER_ID DAWN_FLOW_CONSUMER_ID WATCH_ISSUE_IID; do
    [[ -z ${!name:-} || ${!name} =~ ^[0-9]+$ ]] || die "Expected a numeric flow or issue ID: $name"
  done
else
  [[ ${UNLEASH_URL:-} == "https://gitlab.com/api/v4/feature_flags/unleash/$GITLAB_PROJECT_ID" ]] || die 'Unleash URL does not match this GitLab project.'
fi

credential_dir=$(mktemp -d)
export CLOUDSDK_CONFIG="$credential_dir/gcloud"
trap 'rm -rf "$credential_dir"' EXIT
printf '%s' "$GITLAB_OIDC_TOKEN" > "$credential_dir/oidc.jwt"
unset GITLAB_OIDC_TOKEN
provider="projects/$GCP_PROJECT_NUMBER/locations/global/workloadIdentityPools/$GCP_WIF_POOL/providers/$GCP_WIF_PROVIDER"
gcloud iam workload-identity-pools create-cred-config "$provider" \
  --service-account="$GCP_SERVICE_ACCOUNT" \
  --credential-source-file="$credential_dir/oidc.jwt" --output-file="$credential_dir/external-account.json"
gcloud auth login --cred-file="$credential_dir/external-account.json" --quiet
gcloud config set project "$GCP_PROJECT_ID" --quiet

# The service is created and made public once by Alex, outside the CI identity.
gcloud run services describe "$service" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format=json > "$credential_dir/service.json"
python3 - "$credential_dir/service.json" "$GITLAB_PROJECT_ID" <<'PY'
import json, sys
service = json.load(open(sys.argv[1]))
if service.get('metadata', {}).get('labels', {}).get('lac-owner') != sys.argv[2]:
    raise SystemExit('Cloud Run service ownership does not match this GitLab project.')
PY

image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_ARTIFACT_REPOSITORY/$target:$CI_COMMIT_SHA"
build_id=$(gcloud builds submit . --project="$GCP_PROJECT_ID" --region="$GCP_REGION" \
  --config=deploy/cloudbuild.yaml --ignore-file=deploy/.gcloudignore \
  --gcs-source-staging-dir="gs://$GCP_SOURCE_BUCKET/source" \
  --service-account="projects/$GCP_PROJECT_ID/serviceAccounts/$GCP_BUILD_SERVICE_ACCOUNT" \
  --substitutions="_IMAGE_URI=$image,_COMMIT=$CI_COMMIT_SHORT_SHA,_APP_DIR=$app_dir" \
  --suppress-logs --format='value(id)' --quiet)
[[ $build_id =~ ^[0-9a-f-]{36}$ ]] || die 'Cloud Build did not return a valid build identity.'
digest=$(gcloud builds describe "$build_id" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format='value(results.images[0].digest)')
[[ $digest =~ ^sha256:[0-9a-f]{64}$ ]] || die 'Cloud Build did not return the built image digest.'
immutable_image="${image%:*}@$digest"

python3 - "$credential_dir/public-env.json" "$target" <<'PUBLIC_ENV'
import json, os, sys
from pathlib import Path
names = ('CI_COMMIT_SHORT_SHA', 'APP_ENV', 'UNLEASH_URL')
if sys.argv[2] == 'relay':
    names = ('CI_COMMIT_SHORT_SHA', 'GITLAB_URL', 'GITLAB_PROJECT_ID', 'FLOW_CONSUMER_ID',
             'FLOW_SERVICE_ACCOUNT', 'DAWN_FLOW_CONSUMER_ID', 'WATCH_ISSUE_IID',
             'SHOP_METRICS_URL', 'GCP_PROJECT_ID', 'GCP_REGION', 'STATE_BUCKET', 'STATE_OBJECT')
Path(sys.argv[1]).write_text(json.dumps({name: os.environ.get(name, '') for name in names}))
PUBLIC_ENV
gcloud run deploy "$service" --project="$GCP_PROJECT_ID" --region="$GCP_REGION" \
  --image="$immutable_image" --service-account="$runtime_account" \
  --port=8080 --cpu=1 --memory="$memory" --concurrency=20 --timeout="$request_timeout" \
  --min=0 --min-instances=0 --max-instances=1 \
  "$cpu_flag" --no-cpu-boost --ingress=all \
  --env-vars-file="$credential_dir/public-env.json" --set-secrets="$secret_refs" \
  --labels="lac-owner=$GITLAB_PROJECT_ID,lac-commit=$CI_COMMIT_SHORT_SHA" --quiet
gcloud run services update-traffic "$service" --to-latest --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --quiet
url=$(gcloud run services describe "$service" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format='value(status.url)')
[[ $url == https://*.run.app ]] || die 'Cloud Run did not return its expected public URL.'
# Bound the public health check and verify the served commit, without credentials.
python3 - "$url" "$CI_COMMIT_SHORT_SHA" <<'PY'
import json, sys, urllib.request
with urllib.request.urlopen(sys.argv[1] + '/healthz', timeout=20) as response:
    health = json.loads(response.read(4096))
if health != {'ok': True, 'commit': sys.argv[2]}:
    raise SystemExit('The deployed health response differs from this candidate.')
PY
printf 'DYNAMIC_ENVIRONMENT_URL=%s\n' "$url" > deploy/result.env
python3 - "$url" "$CI_COMMIT_SHA" "$immutable_image" "$build_id" "$target" <<'PY'
import json, sys
from pathlib import Path
Path('deploy/result.json').write_text(json.dumps(dict(zip(
    ('url', 'commit', 'image', 'build_id', 'service'), sys.argv[1:])), indent=2) + '\n')
PY
printf 'Verified %s commit %s at %s\n' "$target" "$CI_COMMIT_SHORT_SHA" "$url"
