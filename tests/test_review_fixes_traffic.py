"""C4 from the review: a Cloud Run traffic change is done only when Cloud Run says so. Offline, against a fake server.

After the PATCH the port reads the long-running operation until it is done, then reads the service back: not
reconciling, its terminal condition succeeded, and its trafficStatuses as wanted. A change that is still running
when the time is up may land later, so it is an ApplyFailed that keeps the snapshot from before it. The clock only
moves when the code sleeps, so no test waits.

Every name, token and time here is test data.
"""

from __future__ import annotations

import httpx
import pytest

from nightorders.gitlab_ports import GitLab, GitLabPorts, Http
from nightorders.model import Action, Change
from test_relay_ports import NOW, SERVICE, TOPIC_URL, Server

OPERATION = "projects/demo-project/locations/us-central1/operations/op-1"
OPERATION_PATH = f"/v2/{OPERATION}"
TRAFFIC = Action(kind="traffic_to_revision", service="shop", revision="shop-00041")
LATEST = [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "percent": 100}]
PINNED = [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION", "revision": "shop-00041", "percent": 100}]
SUCCEEDED = {"state": "CONDITION_SUCCEEDED", "type": "Ready"}


class Clock:
    """A clock that moves only when the code sleeps."""

    def __init__(self):
        self.now, self.slept = 0.0, []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


def in_turn(*answers):
    """A route that gives these answers one after another, then the last one again."""
    queue = list(answers)
    return lambda request: queue.pop(0) if len(queue) > 1 else queue[0]


def service(traffic: list, statuses: list, *, reconciling: bool = False, condition: dict = SUCCEEDED) -> dict:
    return {"name": "projects/demo-project/locations/us-central1/services/shop", "etag": "etag-5",
            "template": {"containers": [{"image": "example/shop@sha256:1"}]}, "traffic": traffic,
            "reconciling": reconciling, "terminalCondition": condition, "trafficStatuses": statuses}


def cloud_run(server: Server, budget: float | None = None) -> tuple[GitLabPorts, Clock]:
    clock = Clock()
    http = Http(httpx.Client(transport=httpx.MockTransport(server)), budget_seconds=budget, clock=clock)
    http.sleep = clock.sleep
    ports = GitLabPorts(GitLab(http, "https://gitlab.example", "123", "test-token"), http, flow_consumer_id="77",
                        flow_service_account="duo-watch", ntfy_url=TOPIC_URL, gcp_project="demo-project",
                        gcp_region="us-central1", google_token=lambda: "test-google-token")
    return ports, clock


def running(done: bool = False, **more) -> dict:
    return {"name": OPERATION, "done": done, **more}


def test_a_traffic_change_waits_for_cloud_run_and_reads_the_traffic_back():
    server = Server({("GET", SERVICE): in_turn(service(LATEST, LATEST), service(PINNED, PINNED)),
                     ("PATCH", SERVICE): running(),
                     ("GET", OPERATION_PATH): in_turn(running(), running(done=True, response={}))})
    ports, clock = cloud_run(server, budget=15)
    change = ports.apply(TRAFFIC, NOW)
    assert change == Change(changed=True, before={"kind": "traffic", "service": "shop", "traffic": LATEST},
                            detail="shop traffic was 100% to the latest revision")
    polls = server.sent("GET", OPERATION_PATH)
    assert len(polls) == 2 and clock.slept == [1.0, 1.0]
    assert all(p.url.host == "run.googleapis.com" and p.headers["Authorization"] == "Bearer test-google-token"
               for p in polls)
    assert len(server.sent("GET", SERVICE)) == 2  # before the change, and after it to read the traffic back


def test_an_operation_that_ends_in_an_error_is_a_failed_change_with_its_snapshot():
    failed = running(done=True, error={"code": 9, "message": "Revision shop-00041 is not ready."})
    server = Server({("GET", SERVICE): service(LATEST, LATEST), ("PATCH", SERVICE): running(),
                     ("GET", OPERATION_PATH): failed})
    ports, _clock = cloud_run(server)
    with pytest.raises(RuntimeError, match="Cloud Run send shop traffic: Revision shop-00041 is not ready.") as error:
        ports.apply(TRAFFIC, NOW)
    assert type(error.value).__name__ == "ApplyFailed"
    assert error.value.before == {"kind": "traffic", "service": "shop", "traffic": LATEST}


@pytest.mark.parametrize("after", [
    service(PINNED, LATEST, condition={"state": "CONDITION_FAILED", "message": "Revision failed."}),
    service(PINNED, LATEST, reconciling=True, condition={"state": "CONDITION_RECONCILING"}),
    service(PINNED, [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION", "revision": "shop-00041", "percent": 50},
                     {"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_REVISION", "revision": "shop-00042", "percent": 50}]),
], ids=["failed", "still reconciling", "half the traffic"])
def test_a_finished_operation_whose_traffic_is_not_serving_is_a_failed_change(after):
    server = Server({("GET", SERVICE): in_turn(service(LATEST, LATEST), after),
                     ("PATCH", SERVICE): running(done=True, response={})})
    ports, _clock = cloud_run(server)
    with pytest.raises(RuntimeError, match="does not report the new traffic as serving") as error:
        ports.apply(TRAFFIC, NOW)
    assert type(error.value).__name__ == "ApplyFailed"
    assert error.value.before == {"kind": "traffic", "service": "shop", "traffic": LATEST}


def test_a_change_still_running_when_the_tick_runs_out_may_land_so_it_keeps_its_snapshot():
    server = Server({("GET", SERVICE): service(LATEST, LATEST), ("PATCH", SERVICE): running(),
                     ("GET", OPERATION_PATH): running()})
    ports, clock = cloud_run(server, budget=5)
    with pytest.raises(RuntimeError, match="had not finished the change when the time ran out") as error:
        ports.apply(TRAFFIC, NOW)
    assert type(error.value).__name__ == "ApplyFailed"  # not NotSent: the PATCH went out
    assert getattr(error.value, "sent", True) is True
    assert error.value.before == {"kind": "traffic", "service": "shop", "traffic": LATEST}
    assert clock.now < 5 and len(server.sent("GET", OPERATION_PATH)) == len(clock.slept) >= 1


def test_a_restore_is_done_only_when_the_traffic_is_back_as_the_snapshot_says():
    # A target that sends traffic to the latest revision may be reported with that revision's name.
    resolved = [{"type": "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST", "revision": "shop-00042", "percent": 100}]
    back = service(LATEST, resolved)
    snapshot = {"kind": "traffic", "service": "shop", "traffic": LATEST}
    server = Server({("GET", SERVICE): in_turn(service(PINNED, PINNED), back), ("PATCH", SERVICE): running(),
                     ("GET", OPERATION_PATH): running(done=True, response={})})
    ports, _clock = cloud_run(server)
    restored = ports.restore(TRAFFIC, snapshot, NOW)
    assert restored.changed is True and restored.detail == "shop traffic is 100% to the latest revision again"

    server = Server({("GET", SERVICE): in_turn(service(PINNED, PINNED), service(LATEST, PINNED)),
                     ("PATCH", SERVICE): running(), ("GET", OPERATION_PATH): running(done=True, response={})})
    ports, _clock = cloud_run(server)
    with pytest.raises(RuntimeError, match="does not report the new traffic as serving") as error:
        ports.restore(TRAFFIC, snapshot, NOW)
    assert type(error.value).__name__ == "ApplyFailed"
    assert error.value.before == {"kind": "traffic", "service": "shop", "traffic": PINNED}  # before the restore
