"""The demo shop's Unleash client for GitLab feature flags. Offline: GitLab is an httpx.MockTransport.

Flag names, user IDs, URLs and answers here are test data. The rollout cases at the bottom come from
Unleash's client specification (https://github.com/Unleash/client-specification, files 01, 02, 03, 10).
"""

import asyncio
import random

import httpx
import pytest

from flags import FlagClient, feature_on, murmur3_32, normalized_value, parse_features

URL = "https://gitlab.example/api/v4/feature_flags/unleash/42"
DEFAULT = {"name": "default", "parameters": {}}


def users(ids: str) -> dict:
    return {"name": "userWithId", "parameters": {"userIds": ids}}


def flag(name: str, *strategies: dict, enabled: bool = True) -> dict:
    return {"name": name, "enabled": enabled, "strategies": list(strategies)}


class FakeGitLab:
    """Answers like GitLab's /client/features endpoint, or fails on request."""

    def __init__(self, *features: dict) -> None:
        self.features = list(features)
        self.fail: str | int | None = None  # "down", an HTTP status, or "garbage"
        self.requests: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if self.fail == "down":
            raise httpx.ConnectError("connection refused", request=request)
        if self.fail == "garbage":
            return httpx.Response(200, json={"message": "not flags"})
        if isinstance(self.fail, int):
            return httpx.Response(self.fail, json={"message": "test failure"})
        return httpx.Response(200, json={"version": 1, "features": self.features})


class Clock:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


def client_for(gitlab: FakeGitLab, clock: Clock | None = None, **kwargs) -> FlagClient:
    return FlagClient(URL, "glffct-test-instance-id", "production", transport=httpx.MockTransport(gitlab.handler),
                      monotonic=clock or Clock(), rng=random.Random(0), **kwargs)


def test_every_flag_is_off_before_the_first_answer():
    client = client_for(FakeGitLab(flag("new_checkout", DEFAULT)))
    assert not client.is_on("new_checkout", "pilot-01")
    assert not client.is_on("stock_from_cache", "pilot-01")
    assert client.summary("new_checkout") == "off"


def test_fetch_uses_gitlab_url_and_headers():
    gitlab = FakeGitLab(flag("new_checkout", DEFAULT))
    client = client_for(gitlab)
    assert asyncio.run(client.refresh()) is True
    request = gitlab.requests[0]
    assert str(request.url) == URL + "/client/features"
    assert request.headers["UNLEASH-INSTANCEID"] == "glffct-test-instance-id"
    assert request.headers["UNLEASH-APPNAME"] == "production"


def test_default_strategy_is_on_for_everyone():
    client = client_for(FakeGitLab(flag("new_checkout", DEFAULT)))
    asyncio.run(client.refresh())
    assert client.is_on("new_checkout", "pilot-01")
    assert client.is_on("new_checkout", "shopper-001")
    assert client.is_on("new_checkout", None)
    assert client.summary("new_checkout") == "on for every user"
    assert client.source("new_checkout") == "GitLab feature flags (production)"


def test_user_with_id_is_on_only_for_listed_users():
    client = client_for(FakeGitLab(flag("new_checkout", users("pilot-01,pilot-02"))))
    asyncio.run(client.refresh())
    assert client.is_on("new_checkout", "pilot-01")
    assert client.is_on("new_checkout", "pilot-02")
    assert not client.is_on("new_checkout", "shopper-001")
    assert not client.is_on("new_checkout", None)
    assert client.summary("new_checkout") == "on for 2 listed users"


def test_disabled_and_missing_flags_are_off():
    client = client_for(FakeGitLab(flag("new_checkout", DEFAULT, enabled=False)))
    asyncio.run(client.refresh())
    assert not client.is_on("new_checkout", "pilot-01")
    assert not client.is_on("stock_from_cache", "pilot-01")  # GitLab leaves out flags with no strategy here
    assert client.summary("stock_from_cache") == "off (not set for this environment)"


def test_unreachable_flag_service_keeps_the_last_known_values():
    gitlab = FakeGitLab(flag("new_checkout", DEFAULT), flag("stock_from_cache", DEFAULT))
    client = client_for(gitlab)
    assert asyncio.run(client.refresh())
    for failure in ("down", 500, 401, "garbage"):
        gitlab.fail = failure
        assert asyncio.run(client.refresh()) is False
        assert client.is_on("new_checkout", "pilot-01"), failure
        assert client.is_on("stock_from_cache", "pilot-01"), failure
        assert client.last_error
    gitlab.fail = None
    gitlab.features = [flag("new_checkout", DEFAULT, enabled=False)]
    assert asyncio.run(client.refresh())
    assert not client.is_on("new_checkout", "pilot-01")
    assert not client.is_on("stock_from_cache", "pilot-01")
    assert client.last_error is None


def test_unreachable_at_start_leaves_every_flag_off(capsys):
    gitlab = FakeGitLab(flag("new_checkout", DEFAULT))
    gitlab.fail = "down"
    client = client_for(gitlab)
    assert asyncio.run(client.refresh()) is False
    assert not client.is_on("new_checkout", "pilot-01")
    assert "Feature flags unreachable" in capsys.readouterr().out


def test_flags_are_cached_for_15_seconds_and_refreshed_in_the_background():
    gitlab = FakeGitLab(flag("new_checkout", DEFAULT))
    clock = Clock()
    client = client_for(gitlab, clock)

    async def scenario() -> list[bool]:
        started = []
        task = client.maybe_refresh()
        started.append(task is not None)
        await task
        clock.t += 14.9
        started.append(client.maybe_refresh() is not None)
        clock.t += 0.2
        task = client.maybe_refresh()
        started.append(task is not None)
        await task
        return started

    assert asyncio.run(scenario()) == [True, False, True]
    assert len(gitlab.requests) == 2


def test_a_failed_fetch_also_waits_15_seconds_before_trying_again():
    gitlab = FakeGitLab()
    gitlab.fail = "down"
    clock = Clock()
    client = client_for(gitlab, clock)

    async def scenario() -> None:
        await client.maybe_refresh()
        for _ in range(5):
            assert client.maybe_refresh() is None
        clock.t += 15
        await client.maybe_refresh()

    asyncio.run(scenario())
    assert len(gitlab.requests) == 2


def test_override_wins_over_gitlab_and_is_labelled():
    gitlab = FakeGitLab(flag("new_checkout", DEFAULT, enabled=False), flag("stock_from_cache", DEFAULT))
    client = client_for(gitlab, overrides={"new_checkout": True, "stock_from_cache": False})
    asyncio.run(client.refresh())
    assert client.is_on("new_checkout", "shopper-001")
    assert not client.is_on("stock_from_cache", "shopper-001")
    assert client.source("new_checkout") == "FLAGS_OVERRIDE (local override)"
    assert client.summary("new_checkout") == "on for every user"


def test_without_a_flag_service_nothing_is_fetched_and_flags_are_off():
    client = FlagClient(None, None, "production")
    assert not client.configured
    assert asyncio.run(_maybe(client)) is None
    assert not client.is_on("new_checkout", "pilot-01")
    assert client.source("new_checkout") == "default off (no flag service set)"


async def _maybe(client: FlagClient):
    return client.maybe_refresh()


def test_malformed_answers_are_rejected():
    for bad in ([], {"features": "x"}, {"features": [{"enabled": True}]}, {"features": [{"name": "a", "strategies": 3}]}):
        with pytest.raises(ValueError):
            parse_features(bad)


def test_murmur3_matches_reference_values():
    assert murmur3_32(b"") == 0
    assert murmur3_32(b"hello") == 0x248BFA47
    assert murmur3_32(b"The quick brown fox jumps over the lazy dog") == 0x2E4FF723


RNG = random.Random(0)
SPEC_CASES = [
    # (strategies, enabled, user id, expected) from the Unleash client specification
    ([{"name": "default"}], True, None, True),
    ([{"name": "default"}], False, None, False),
    ([], True, None, True),
    ([users("123")], True, "123", True),
    ([users("123")], True, "22", False),
    ([users("123")], True, None, False),
    ([users("123"), {"name": "default"}], True, "22", True),
    ([users("123, 222, 88")], True, "222", True),
    ([{"name": "gradualRolloutUserId", "parameters": {"percentage": "100", "groupId": "AB12A"}}], True, "123", True),
    ([{"name": "gradualRolloutUserId", "parameters": {"percentage": "100", "groupId": "AB12A"}}], True, None, False),
    ([{"name": "gradualRolloutUserId", "parameters": {"percentage": "50", "groupId": "AB12A"}}], True, "122", True),
    ([{"name": "gradualRolloutUserId", "parameters": {"percentage": "50", "groupId": "AB12A"}}], True, "155", False),
    ([{"name": "gradualRolloutUserId", "parameters": {"percentage": "0", "groupId": "AB12A"}}], True, "122", False),
    ([{"name": "gradualRolloutUserId", "parameters": {"percentage": "0", "groupId": "AB12A"}}, {"name": "default"}],
     True, None, True),
    ([{"name": "flexibleRollout", "parameters": {"rollout": "100", "stickiness": "default",
                                                 "groupId": "Feature.flexibleRollout.100"}}], True, None, True),
    ([{"name": "flexibleRollout", "parameters": {"rollout": "10", "stickiness": "default",
                                                 "groupId": "Feature.flexibleRollout.10"}}], True, "174", True),
    ([{"name": "flexibleRollout", "parameters": {"rollout": "10", "stickiness": "default",
                                                 "groupId": "Feature.flexibleRollout.10"}}], True, "499", False),
    ([{"name": "flexibleRollout", "parameters": {"rollout": "55", "stickiness": "userId",
                                                 "groupId": "Feature.flexibleRollout.userId.55"}}], True, "25", True),
    ([{"name": "flexibleRollout", "parameters": {"rollout": "55", "stickiness": "userId",
                                                 "groupId": "Feature.flexibleRollout.userId.55"}}], True, None, False),
    ([{"name": "flexibleRollout", "parameters": {"rollout": "0", "stickiness": "default",
                                                 "groupId": "Feature.flexibleRollout.0"}}], True, "12", False),
    ([{"name": "gradualRolloutRandom", "parameters": {"percentage": "100"}}], True, "123", False),  # unknown here
]


@pytest.mark.parametrize("strategies,enabled,user,expected", SPEC_CASES)
def test_strategies_match_the_unleash_client_specification(strategies, enabled, user, expected):
    feature = {"enabled": enabled, "strategies": strategies}
    assert feature_on(feature, user, "Feature.X", RNG) is expected


def test_normalized_value_is_stable_and_in_range():
    assert normalized_value("122", "AB12A") == 23
    assert normalized_value("155", "AB12A") == 100
    assert all(1 <= normalized_value(f"user-{n}", "new_checkout") <= 100 for n in range(500))
