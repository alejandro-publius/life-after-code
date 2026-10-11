#!/usr/bin/env python3
"""Owned Scheduler and relay uptime resources, using the official REST APIs.

https://cloud.google.com/scheduler/docs/reference/rest/v1/projects.locations.jobs
https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.uptimeCheckConfigs
https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.alertPolicies
https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.notificationChannels
https://cloud.google.com/secret-manager/docs/access-secret-version

Email, access tokens, and the Scheduler header remain only in request memory.
The journal stores resource names, never request bodies or response objects.
"""

import base64
import getpass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request


class SetupError(Exception):
    """A safe explanation that contains no request or response payload."""


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise SetupError("Cloud API redirect refused.")


class CloudApi:
    HOSTS = {
        "scheduler": "cloudscheduler.googleapis.com/v1/",
        "monitoring": "monitoring.googleapis.com/v3/",
        "secrets": "secretmanager.googleapis.com/v1/",
    }

    def __init__(self, project):
        environment = dict(os.environ, CLOUDSDK_CORE_LOG_HTTP="false",
                           CLOUDSDK_CORE_VERBOSITY="error")
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token", "--quiet"],
            capture_output=True, text=True, timeout=60, env=environment,
            check=False,
        )
        self.token = result.stdout.strip()
        if result.returncode or not self.token or re.search(r"\s", self.token):
            raise SetupError("Google authentication failed. No credentials were printed.")
        self.project = project
        self.deadline = time.monotonic() + 600
        self.opener = urllib.request.build_opener(NoRedirect)

    def call(self, api, method, path, body=None, query=None, missing_ok=False):
        # Callers pass a resource path, never an arbitrary URL or alternate host.
        if not path.startswith("projects/") or ".." in path or "?" in path:
            raise SetupError("Invalid Cloud API resource path.")
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise SetupError("Operations reached the ten minute time limit.")
        url = "https://" + self.HOSTS[api] + path
        if query:
            url += "?" + urllib.parse.urlencode(query)
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(
            url, data=data, method=method,
            headers={"Authorization": "Bearer " + self.token,
                     "Content-Type": "application/json",
                     "X-Goog-User-Project": self.project},
        )
        try:
            with self.opener.open(request, timeout=min(60, remaining)) as response:
                raw = response.read(8 * 1024 * 1024 + 1)
                if len(raw) > 8 * 1024 * 1024:
                    raise SetupError("Cloud API response exceeded the size limit.")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as error:
            if error.code == 404 and missing_ok:
                return None
            # API errors can echo headers or email. Never display their bodies.
            raise SetupError(f"Cloud API {method} failed with HTTP {error.code}. "
                             "Request and response values were not printed.") from None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            raise SetupError("Cloud API transport or JSON failed. "
                             "Request and response values were not printed.") from None

    def listing(self, api, path, field):
        items, page = [], None
        for _ in range(100):
            result = self.call(api, "GET", path,
                               query={"pageToken": page} if page else None)
            items.extend(result.get(field, []))
            page = result.get("nextPageToken")
            if not page:
                return items
        raise SetupError("Cloud API listing exceeded the page limit.")


class Journal:
    def __init__(self, path, source_bucket):
        self.path = Path(path)
        self.bucket = source_bucket
        self.value = json.loads(self.path.read_text())
        self.value.setdefault("ops", {})

    def save(self):
        descriptor, temporary = tempfile.mkstemp(
            prefix=self.path.name + ".", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w") as output:
                json.dump(self.value, output, indent=2, sort_keys=True)
                output.write("\n")
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        result = subprocess.run(
            ["gcloud", "storage", "cp", str(self.path),
             "gs://" + self.bucket + "/bootstrap/state.json",
             "--project=" + self.value["config"]["GCP_PROJECT_ID"], "--quiet"],
            capture_output=True, text=True, timeout=60, check=False,
        )
        if result.returncode:
            raise SetupError("Ownership backup failed. The local journal was retained.")

    def owns(self, kind):
        return kind in self.value["resources"]

    def intent(self, kind):
        if not self.owns(kind):
            self.value["resources"].append(kind)
            self.save()

    def record(self, kind, name):
        self.value["ops"][kind] = name
        self.save()


class Operations:
    KINDS = {
        "notification-channel": ("notificationChannels", "notificationChannels"),
        "uptime-check": ("uptimeCheckConfigs", "uptimeCheckConfigs"),
        "alert-policy": ("alertPolicies", "alertPolicies"),
    }

    def __init__(self, cloud, journal, project, region, gitlab_id, description, project_number=None):
        self.cloud, self.journal = cloud, journal
        self.project, self.region = project, region
        self.gitlab_id, self.description = gitlab_id, description
        self.parent = "projects/" + project
        self.parents = [self.parent]
        if project_number:
            self.parents.append("projects/" + project_number)
        self.labels = {"lac_owner": gitlab_id}

    def display(self, kind):
        return f"Night Orders relay {kind} GitLab {self.gitlab_id}"

    def validate_name(self, kind, name):
        if kind == "scheduler-job":
            expected = [f"{parent}/locations/{self.region}/jobs/relay-tick" for parent in self.parents]
            if name not in expected:
                raise SetupError("Scheduler journal name does not match this project.")
        else:
            collection = self.KINDS[kind][0]
            if not any(re.fullmatch(re.escape(parent + "/" + collection + "/")
                                    + r"[A-Za-z0-9_-]+", name) for parent in self.parents):
                raise SetupError("Monitoring journal name does not match this project.")

    def verify(self, kind, resource):
        self.validate_name(kind, resource["name"])
        owned = (resource.get("description") == self.description if kind == "scheduler-job"
                 else resource.get("userLabels", {}).get("lac_owner") == self.gitlab_id)
        if not owned or not self.journal.owns(kind):
            raise SetupError("Resource ownership collision: " + kind)

    def find(self, kind):
        saved = self.journal.value["ops"].get(kind)
        if kind == "scheduler-job":
            name = saved or f"{self.parent}/locations/{self.region}/jobs/relay-tick"
            self.validate_name(kind, name)
            found = self.cloud.call("scheduler", "GET", name, missing_ok=True)
            if found is not None:
                self.verify(kind, found)
            return found
        collection, field = self.KINDS[kind]
        if saved:
            self.validate_name(kind, saved)
            found = self.cloud.call("monitoring", "GET", saved, missing_ok=True)
            if found is not None:
                self.verify(kind, found)
                return found
        candidates = [item for item in self.cloud.listing(
            "monitoring", self.parent + "/" + collection, field)
            if item.get("displayName") == self.display(kind)]
        if len(candidates) > 1:
            raise SetupError("Several resources use the expected display name: " + kind)
        if candidates:
            self.verify(kind, candidates[0])
            return candidates[0]
        return None

    def upsert(self, kind, body, mask):
        found = self.find(kind)
        api = "scheduler" if kind == "scheduler-job" else "monitoring"
        collection = (self.parent + "/locations/" + self.region + "/jobs"
                      if kind == "scheduler-job" else self.parent + "/" + self.KINDS[kind][0])
        if kind == "scheduler-job" and (not found or self.journal.value.get("ops_scheduler_pending")):
            # Create with an annual holding schedule, pause, then apply the real cron.
            # Persist the intent so an interrupted create cannot become an active tick.
            self.journal.value["ops_scheduler_pending"] = True
            self.journal.intent(kind)
            self.journal.save()
            if not found:
                holding = dict(body, schedule="0 0 1 1 *")
                found = self.cloud.call(api, "POST", collection, holding)
                self.validate_name(kind, found["name"])
                self.journal.record(kind, found["name"])
            if found.get("state") != "PAUSED":
                self.cloud.call(api, "POST", found["name"] + ":pause", {})
        if found:
            body["name"] = found["name"]
            response = self.cloud.call(api, "PATCH", found["name"], body,
                                       query={"updateMask": mask})
        else:
            self.journal.intent(kind)
            response = self.cloud.call(api, "POST", collection, body)
        self.validate_name(kind, response["name"])
        self.journal.record(kind, response["name"])
        if kind == "scheduler-job" and self.journal.value.get("ops_scheduler_pending"):
            self.journal.value["ops_scheduler_pending"] = False
            self.journal.save()
        return response["name"]

    def setup(self, relay_url, alert_email, secret_id):
        host = urllib.parse.urlsplit(relay_url)
        if (host.scheme != "https" or not host.hostname
                or not host.hostname.endswith(".run.app") or host.username
                or host.password or host.port or host.query or host.fragment
                or host.path not in ("", "/")):
            raise SetupError("RELAY_URL must be the HTTPS Cloud Run service URL.")
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", alert_email):
            raise SetupError("Enter a valid alert email address.")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,255}", secret_id):
            raise SetupError("Invalid relay Secret Manager name.")
        secret = self.cloud.call(
            "secrets", "GET", f"{self.parent}/secrets/{secret_id}/versions/latest:access")
        try:
            relay_key = base64.b64decode(secret["payload"]["data"], validate=True).decode()
        except (KeyError, ValueError, UnicodeError):
            raise SetupError("The relay key secret is not valid text.") from None
        if not re.fullmatch(r"[A-Za-z0-9_-]{24,256}", relay_key):
            raise SetupError("The relay key secret is not a valid generated key.")
        job_name = f"{self.parent}/locations/{self.region}/jobs/relay-tick"
        self.upsert("scheduler-job", {
            "name": job_name, "description": self.description,
            "schedule": "* * * * *", "timeZone": "Etc/UTC",
            "httpTarget": {"uri": relay_url.rstrip("/") + "/tick",
                           "httpMethod": "POST", "headers": {"X-Relay-Key": relay_key}},
            "attemptDeadline": "60s",
            "retryConfig": {"retryCount": 0, "maxRetryDuration": "0s"},
        }, "description,schedule,timeZone,httpTarget,attemptDeadline,retryConfig")
        # Do not retain the header in a state file or display the API response.
        channel = self.upsert("notification-channel", {
            "type": "email", "displayName": self.display("notification-channel"),
            "description": self.description, "userLabels": self.labels,
            "labels": {"email_address": alert_email}, "enabled": True,
        }, "displayName,description,userLabels,labels,enabled")
        check = self.upsert("uptime-check", {
            "displayName": self.display("uptime-check"), "userLabels": self.labels,
            "monitoredResource": {"type": "uptime_url",
                                  "labels": {"project_id": self.project, "host": host.hostname}},
            "httpCheck": {"requestMethod": "GET", "useSsl": True,
                          "validateSsl": True, "port": 443, "path": "/healthz"},
            "period": "60s", "timeout": "10s", "selectedRegions": ["USA"],
        }, "displayName,userLabels,monitoredResource,httpCheck,period,timeout,selectedRegions")
        check_id = check.rsplit("/", 1)[1]
        self.upsert("alert-policy", {
            "displayName": self.display("alert-policy"), "userLabels": self.labels,
            "enabled": True, "combiner": "OR", "notificationChannels": [channel],
            "documentation": {"mimeType": "text/markdown", "content":
                              "Night Orders relay /healthz has failed for two minutes. "
                              "Check the relay before relying on overnight automation."},
            "conditions": [{"displayName": "Relay health check fails for two minutes",
                            "conditionThreshold": {
                                "filter": 'metric.type="monitoring.googleapis.com/uptime_check/check_passed" '
                                          'AND resource.type="uptime_url" '
                                          f'AND metric.labels.check_id="{check_id}"',
                                "aggregations": [{"alignmentPeriod": "60s",
                                                  "perSeriesAligner": "ALIGN_FRACTION_TRUE"}],
                                "comparison": "COMPARISON_LT", "thresholdValue": 1,
                                "duration": "120s", "trigger": {"count": 1},
                                "evaluationMissingData": "EVALUATION_MISSING_DATA_INACTIVE",
                            }}],
            "alertStrategy": {"autoClose": "1800s"},
        }, "displayName,userLabels,enabled,combiner,notificationChannels,documentation,conditions,alertStrategy")

    def teardown(self):
        for kind in ("scheduler-job", "alert-policy", "uptime-check", "notification-channel"):
            if not self.journal.owns(kind):
                continue
            found = self.find(kind)
            if found:
                self.cloud.call("scheduler" if kind == "scheduler-job" else "monitoring",
                                "DELETE", found["name"])
            self.journal.value["ops"].pop(kind, None)
            self.journal.save()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("setup", "teardown"):
        raise SetupError("Usage: monitoring.py setup or teardown")
    journal = Journal(os.environ["LAC_OPS_STATE_FILE"], os.environ["LAC_OPS_SOURCE_BUCKET"])
    config = journal.value["config"]
    for key in ("GCP_PROJECT_ID", "GCP_REGION", "GITLAB_PROJECT_ID"):
        if os.environ.get(key) != config[key]:
            raise SetupError("Operations environment differs from the ownership journal.")
    cloud = CloudApi(config["GCP_PROJECT_ID"])
    operations = Operations(cloud, journal, config["GCP_PROJECT_ID"], config["GCP_REGION"],
                            config["GITLAB_PROJECT_ID"], os.environ["LAC_OPS_OWNER_DESCRIPTION"],
                            config["GCP_PROJECT_NUMBER"])
    if sys.argv[1] == "setup":
        email = os.environ.get("ALERT_EMAIL", "")
        if not email:
            email = getpass.getpass("Email for relay health alerts (not saved locally): ")
        operations.setup(os.environ["RELAY_URL"], email, os.environ.get("GCP_RELAY_KEY_SECRET", "relay-key"))
        print("Owned relay Scheduler job, uptime check, and email alert are ready. "
              "New Scheduler jobs remain paused until the day-one test.")
    else:
        operations.teardown()
        print("Owned relay Scheduler and Monitoring resources were removed.")


if __name__ == "__main__":
    try:
        main()
    except (SetupError, KeyError, ValueError, OSError, subprocess.TimeoutExpired):
        # Unexpected validation failures must not dump exception objects holding values.
        exception = sys.exception()
        print(str(exception) if isinstance(exception, SetupError)
              else "Operations setup failed. Sensitive values were not printed.", file=sys.stderr)
        raise SystemExit(1) from None
