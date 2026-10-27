# Container release verification

The default-branch pipeline builds and pushes both the relay and shop, scans the exact manifest digests it
pushed, and prevents a tagged GitLab Release when either image fails policy. A successful scanner process
alone is not a clean vulnerability result.

## Evidence and dependencies

1. `package_images` builds both services from `deploy/Dockerfile`, using the full commit SHA as the registry
   tag. A failed build or push fails the job. For each push it reads the registry manifest digest from Docker's
   output, pulls that immutable reference back from the registry, and records Docker's `RepoDigests`.
2. The packaging artifacts contain one JSON receipt per service with the full commit, pipeline ID, tag,
   immutable image reference and SHA256 manifest digest. A dotenv artifact supplies `RELAY_SCAN_IMAGE` and
   `SHOP_SCAN_IMAGE` to the dependent scanner jobs.
3. `container_scanning` scans the relay; `container_scanning_shop` scans the shop. Both invoke GitLab's
   `gtcs scan` with the digest reference, include unfixed and language-package findings, and fail if the analyzer
   exits unsuccessfully. They retain reports in separate paths, so downloading both cannot overwrite one.
4. Each scanner invocation records its exact image, commit, pipeline, exit status and SHA256 of the original
   report bytes. The scanner job uses shell tools; it does not assume Python is installed in the analyzer image.
5. `container_policy` runs in its own Python 3.12 job and requires evidence for **both** services. It fails on
   missing or malformed evidence, invalid or mismatched manifest digests, mismatched registry readback,
   another commit or pipeline, analyzer failure, modified report bytes, unsuccessful or partial scans, wrong
   images in findings, missing/unknown severities, and any **High or Critical** finding. Lower classified
   findings remain counted in the policy artifact.
6. `release` explicitly requires this policy plus the application tests, deployment fixture tests, browser
   smoke, lint, dependency audit, demo replay, order/state/flow validation, CLI audit and Pages artifact. None
   of these release dependencies is optional. Pages serves the labelled browser demo independently; container
   policy controls the tagged release, not access to the existing demo.

The template's normal `allow_failure: true` setting is overridden for image packaging and both container
scans. `container_policy` runs even after an earlier failure so it can retain a failed evidence report.

## What a clean report proves

GitLab's [container report schema](https://gitlab.com/gitlab-org/security-products/security-report-schemas/-/blob/master/dist/container-scanning-report-format.json)
places the image in each vulnerability's `location.image`. It has no top-level image or `scan.target` field.
An image with zero findings consequently has no native image field in that report. The invocation receipt
binds even an empty report to the digest actually passed to `gtcs`, and to this pipeline, by hashing the
unmodified report. Findings that are present must independently name that same immutable image.

These receipts are pipeline provenance, not cryptographic signatures or attestations from an independent
authority. They rely on the trusted runner and CI configuration. The gate does not prove absence of unknown
vulnerabilities or validate a production rollout. A High/Critical finding requires a dependency or base-image
fix and a new scan; a scanner exit code of zero does not waive it.

Sources: GitLab's [container scanning template](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Jobs/Container-Scanning.gitlab-ci.yml),
[analyzer scan implementation](https://gitlab.com/gitlab-org/security-products/analyzers/container-scanning/-/blob/master/lib/gcs/scan.rb),
and [container scanning configuration](https://docs.gitlab.com/user/application_security/container_scanning/).

## Local verification and current limit

The corrected images were built and exercised locally from `2df2e4afa28dbe2a2c0bf73b536fa833d425cc0c`.
Both ran as UID 10001 and contained `certifi 2026.10.23` and `opentelemetry-api 1.45.1`, matching the audited
runtime lock. Both morning replay choices, captured execution data and a real HTTP shop checkout passed.
[Exact image IDs, installed versions and results](codex/packaged-runtime.json). This closes the previously
observed drift in both packaged requirement files. It is local image execution, not registry publication or
a GitLab container-analyzer scan.

From the repository root:

```sh
uv run --locked pytest -q tests/test_container_policy.py tests/test_pipeline_config.py
```

The policy tests use labelled synthetic GitLab reports and CI receipts. They exercise both clean images,
High/Critical findings in either service, missing reports, scanner failures, changed report bytes, wrong
images/digests, wrong commit or pipeline, and the command's failing exit status. The shell contract tests run
the actual packaging/scanning scripts against local Docker/analyzer doubles; they do not claim to push or
scan a real container.

The previous [pipeline 2994456180](https://gitlab.com/gitlab-ai-hackathon/transcend-october-2026/43649347/showcase/-/pipelines/2994456180)
completed all 18 jobs successfully under the previous configuration. It is historical evidence, not a run of
these new gates. The project is currently archived and GitLab pushes are blocked. Live CI linting, image
publication, scanner/report compatibility and release gating for this change remain **unverified on GitLab**.
They require an authorized project administrator to restore write access, followed by a new pipeline. No new
GitLab project or permission expansion is part of this change.
