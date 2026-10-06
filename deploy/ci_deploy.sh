#!/usr/bin/env bash
# Authenticate temporarily, build remotely and update the bootstrapped service.
set -euo pipefail
umask 077

die() { printf '%s\n' "$*" >&2; exit 1; }
[[ ${CI_DEBUG_TRACE:-false} != true ]] || die 'Disable CI debug tracing before using credentials.'
for name in GCP_PROJECT_ID GCP_PROJECT_NUMBER GCP_REGION GCP_WIF_POOL GCP_WIF_PROVIDER \
  GCP_SERVICE_ACCOUNT GCP_BUILD_SERVICE_ACCOUNT GCP_RUNTIME_SERVICE_ACCOUNT \
  GCP_ARTIFACT_REPOSITORY GCP_SOURCE_BUCKET GCP_RUN_SERVICE GITLAB_PROJECT_ID \
  GITLAB_PROJECT_PATH GITLAB_OIDC_TOKEN CI_COMMIT_SHA CI_COMMIT_SHORT_SHA CI_PROJECT_ID CI_PROJECT_PATH \
  CI_COMMIT_BRANCH CI_DEFAULT_BRANCH CI_COMMIT_REF_PROTECTED; do
  [[ -n ${!name:-} ]] || die "Missing required CI variable: $name"
done
[[ $CI_PROJECT_ID == "$GITLAB_PROJECT_ID" && $CI_PROJECT_PATH == "$GITLAB_PROJECT_PATH" ]] || die 'The GitLab project does not match the configured trust.'
[[ ${CI_COMMIT_BRANCH:-} == "${CI_DEFAULT_BRANCH:-}" && ${CI_COMMIT_REF_PROTECTED:-false} == true ]] || die 'Only the protected default branch may deploy.'
[[ $CI_COMMIT_SHA =~ ^[0-9a-f]{40}$ && $CI_COMMIT_SHORT_SHA =~ ^[0-9a-f]{7,40}$ ]] || die 'Invalid candidate commit identity.'
[[ $GCP_PROJECT_ID =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ && $GCP_PROJECT_NUMBER =~ ^[0-9]+$ ]] || die 'Invalid Google project identity.'
for name in GCP_REGION GCP_WIF_POOL GCP_WIF_PROVIDER GCP_ARTIFACT_REPOSITORY GCP_SOURCE_BUCKET GCP_RUN_SERVICE; do
  [[ ${!name} =~ ^[a-z0-9][a-z0-9-]+[a-z0-9]$ ]] || die "Invalid resource name: $name"
done
for name in GCP_SERVICE_ACCOUNT GCP_BUILD_SERVICE_ACCOUNT GCP_RUNTIME_SERVICE_ACCOUNT; do
  [[ ${!name} == *@"$GCP_PROJECT_ID".iam.gserviceaccount.com ]] || die "Wrong project for service account: $name"
done

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
gcloud run services describe "$GCP_RUN_SERVICE" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format=json > "$credential_dir/service.json"
python3 - "$credential_dir/service.json" "$GITLAB_PROJECT_ID" <<'PY'
import json, sys
service = json.load(open(sys.argv[1]))
if service.get('metadata', {}).get('labels', {}).get('lac-owner') != sys.argv[2]:
    raise SystemExit('Cloud Run service ownership does not match this GitLab project.')
PY

image="$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_ARTIFACT_REPOSITORY/app:$CI_COMMIT_SHA"
build_id=$(gcloud builds submit . --project="$GCP_PROJECT_ID" --region="$GCP_REGION" \
  --config=deploy/cloudbuild.yaml --ignore-file=deploy/.gcloudignore \
  --gcs-source-staging-dir="gs://$GCP_SOURCE_BUCKET/source" \
  --service-account="projects/$GCP_PROJECT_ID/serviceAccounts/$GCP_BUILD_SERVICE_ACCOUNT" \
  --substitutions="_IMAGE_URI=$image,_COMMIT=$CI_COMMIT_SHORT_SHA" \
  --suppress-logs --format='value(id)' --quiet)
[[ $build_id =~ ^[0-9a-f-]{36}$ ]] || die 'Cloud Build did not return a valid build identity.'
digest=$(gcloud builds describe "$build_id" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format='value(results.images[0].digest)')
[[ $digest =~ ^sha256:[0-9a-f]{64}$ ]] || die 'Cloud Build did not return the built image digest.'
immutable_image="${image%:*}@$digest"

gcloud run deploy "$GCP_RUN_SERVICE" --project="$GCP_PROJECT_ID" --region="$GCP_REGION" \
  --image="$immutable_image" --service-account="$GCP_RUNTIME_SERVICE_ACCOUNT" \
  --port=8080 --cpu=1 --memory=256Mi --concurrency=20 --timeout=30s \
  --min=0 --max=1 --min-instances=0 --max-instances=1 \
  --cpu-throttling --no-cpu-boost --ingress=all \
  --update-env-vars="CI_COMMIT_SHORT_SHA=$CI_COMMIT_SHORT_SHA" \
  --labels="lac-owner=$GITLAB_PROJECT_ID,lac-commit=$CI_COMMIT_SHORT_SHA" --quiet
gcloud run services update-traffic "$GCP_RUN_SERVICE" --to-latest --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --quiet
url=$(gcloud run services describe "$GCP_RUN_SERVICE" --region="$GCP_REGION" --project="$GCP_PROJECT_ID" --format='value(status.url)')
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
python3 - "$url" "$CI_COMMIT_SHA" "$immutable_image" "$build_id" <<'PY'
import json, sys
from pathlib import Path
Path('deploy/result.json').write_text(json.dumps(dict(zip(
    ('url', 'commit', 'image', 'build_id'), sys.argv[1:])), indent=2) + '\n')
PY
printf 'Verified deployed commit %s at %s\n' "$CI_COMMIT_SHORT_SHA" "$url"
