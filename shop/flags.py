"""A small Unleash client for GitLab feature flags, written with httpx (no SDK).

GitLab serves its feature flags through an Unleash-compatible API. What this client relies on, read on
2026-10-06 from GitLab's docs and source (https://gitlab.com/gitlab-org/gitlab: doc/operations/feature_flags.md,
lib/api/unleash.rb, lib/api/entities/unleash_feature.rb, app/models/operations/feature_flags_client.rb,
app/models/operations/feature_flags/strategy.rb, spec/requests/api/unleash_spec.rb):

- The API URL looks like https://gitlab.com/api/v4/feature_flags/unleash/<project id>. GitLab shows it,
  with the instance ID, under Deploy > Feature flags > Configure.
- GET {API URL}/client/features with the headers UNLEASH-INSTANCEID (the instance ID) and UNLEASH-APPNAME
  (the environment, for example production). Without an app name GitLab returns no flags; a wrong
  instance ID gets 401.
- The answer is {"version": 1, "features": [{"name", "enabled", "strategies": [{"name", "parameters"}]}]}.
  GitLab lists only flags that have a strategy for this environment, so a flag missing here is off.
- Strategies: default (all users), userWithId (user IDs and user lists, {"userIds": "a,b"}),
  gradualRolloutUserId ({"groupId", "percentage"}) and flexibleRollout ({"groupId", "rollout", "stickiness"}).

Percent strategies use Unleash's hash: MurmurHash3 (x86, 32 bit, seed 0) of "groupId:id", mod 100, plus 1.
The tests check it against https://github.com/Unleash/client-specification.

Flags are cached for 15 seconds. A refresh never makes a customer wait: a request that finds the cache old
starts one in the background. If GitLab cannot be reached, the last known values stay. At start every flag
is off until the first good answer.
"""

from __future__ import annotations

import asyncio
import random
import time
from datetime import datetime, timezone
from typing import Callable

import httpx

import jsonlog

KNOWN_FLAGS = ("new_checkout", "stock_from_cache")
REFRESH_SECONDS = 15.0
TIMEOUT_SECONDS = 3.0


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def murmur3_32(data: bytes, seed: int = 0) -> int:
    """MurmurHash3, x86 32-bit variant, as Unleash clients use it."""
    c1, c2, mask = 0xCC9E2D51, 0x1B873593, 0xFFFFFFFF
    h = seed & mask
    length = len(data)
    end = length - length % 4
    for i in range(0, end, 4):
        k = int.from_bytes(data[i:i + 4], "little")
        k = (k * c1) & mask
        k = ((k << 15) | (k >> 17)) & mask
        k = (k * c2) & mask
        h ^= k
        h = ((h << 13) | (h >> 19)) & mask
        h = (h * 5 + 0xE6546B64) & mask
    tail = data[end:]
    k = 0
    if len(tail) >= 3:
        k ^= tail[2] << 16
    if len(tail) >= 2:
        k ^= tail[1] << 8
    if tail:
        k ^= tail[0]
        k = (k * c1) & mask
        k = ((k << 15) | (k >> 17)) & mask
        k = (k * c2) & mask
        h ^= k
    h ^= length
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & mask
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & mask
    h ^= h >> 16
    return h


def normalized_value(key: str, group_id: str) -> int:
    """A number from 1 to 100 that is stable for one key in one group."""
    return murmur3_32(f"{group_id}:{key}".encode("utf-8")) % 100 + 1


def _in_rollout(key: str, group_id: str, percentage: object) -> bool:
    try:
        share = float(percentage)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False
    return share > 0 and normalized_value(key, group_id) <= share


def strategy_on(strategy: dict, user_id: str | None, flag: str, rng: random.Random) -> bool:
    """Whether one strategy turns the flag on for this user. Unknown strategies are off, as in Unleash."""
    name = strategy.get("name")
    params = strategy.get("parameters") or {}
    if name == "default":
        return True
    if name == "userWithId":
        ids = [part.strip() for part in str(params.get("userIds") or "").split(",")]
        return user_id is not None and user_id in ids
    if name == "gradualRolloutUserId":
        return bool(user_id) and _in_rollout(user_id, str(params.get("groupId") or ""), params.get("percentage"))
    if name == "flexibleRollout":
        stickiness = params.get("stickiness") or "default"
        if stickiness in ("default", "userId"):
            key = user_id or (str(rng.randint(1, 10000)) if stickiness == "default" else None)
        elif stickiness == "random":
            key = str(rng.randint(1, 10000))
        else:
            key = None  # sessionId and custom fields: the shop has neither
        return bool(key) and _in_rollout(key, str(params.get("groupId") or flag), params.get("rollout"))
    return False


def feature_on(feature: dict | None, user_id: str | None, flag: str, rng: random.Random) -> bool:
    if not feature or not feature.get("enabled"):
        return False
    strategies = feature.get("strategies") or []
    if not strategies:
        return True  # Unleash's rule for an enabled flag with no strategies. GitLab does not send one.
    return any(strategy_on(s, user_id, flag, rng) for s in strategies)


def describe_strategy(strategy: dict) -> str:
    name = strategy.get("name")
    params = strategy.get("parameters") or {}
    if name == "default":
        return "on for every user"
    if name == "userWithId":
        count = len([p for p in str(params.get("userIds") or "").split(",") if p.strip()])
        return f"on for {count} listed user{'' if count == 1 else 's'}"
    if name == "gradualRolloutUserId":
        return f"on for {params.get('percentage')}% of users"
    if name == "flexibleRollout":
        return f"on for {params.get('rollout')}% of users ({params.get('stickiness') or 'default'})"
    return f"{name} (not supported here, counts as off)"


def parse_features(data: object) -> dict[str, dict]:
    """The flags in an Unleash answer, by name. Raises ValueError if it is not one."""
    if not isinstance(data, dict) or not isinstance(data.get("features"), list):
        raise ValueError("not an Unleash features answer")
    features: dict[str, dict] = {}
    for item in data["features"]:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise ValueError("a feature without a name")
        strategies = item.get("strategies") or []
        if not isinstance(strategies, list):
            raise ValueError(f"strategies of {item['name']} are not a list")
        features[item["name"]] = {
            "enabled": item.get("enabled") is True,
            "strategies": [s for s in strategies if isinstance(s, dict)],
        }
    return features


def _describe_error(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    return f"{type(exc).__name__}: {exc}"[:200]


class FlagClient:
    """Feature flags for one environment, from GitLab, with an optional local override per flag."""

    def __init__(
        self,
        url: str | None,
        instance_id: str | None,
        environment: str,
        *,
        overrides: dict[str, bool] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        refresh_seconds: float = REFRESH_SECONDS,
        timeout: float = TIMEOUT_SECONDS,
        monotonic: Callable[[], float] = time.monotonic,
        now: Callable[[], datetime] = utcnow,
        rng: random.Random | None = None,
    ) -> None:
        self.url = (url or "").strip().rstrip("/")
        self.instance_id = (instance_id or "").strip()
        self.environment = environment
        self.overrides = dict(overrides or {})
        self.refresh_seconds = refresh_seconds
        self.timeout = timeout
        self.features: dict[str, dict] = {}  # the last good answer; empty means every flag is off
        self.fetched_at: datetime | None = None
        self.last_error: str | None = None
        self._transport = transport
        self._monotonic = monotonic
        self._now = now
        self._rng = rng or random.Random()
        self._attempted: float | None = None
        self._task: asyncio.Task | None = None

    @property
    def configured(self) -> bool:
        return bool(self.url and self.instance_id)

    def is_on(self, name: str, user_id: str | None = None) -> bool:
        if name in self.overrides:
            return self.overrides[name]
        return feature_on(self.features.get(name), user_id, name, self._rng)

    async def refresh(self) -> bool:
        """Fetch the flags once. On any failure keep the last known values. Returns whether it worked."""
        self._attempted = self._monotonic()
        try:
            async with httpx.AsyncClient(transport=self._transport, timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.url}/client/features",
                    headers={
                        "UNLEASH-INSTANCEID": self.instance_id,
                        "UNLEASH-APPNAME": self.environment,
                        "User-Agent": "juniper-market-demo-shop",
                    },
                )
            response.raise_for_status()
            features = parse_features(response.json())
        except Exception as exc:  # unreachable, refused or malformed: all keep the last known values
            text = _describe_error(exc)
            if self.last_error is None:
                jsonlog.emit("WARNING", f"Feature flags unreachable, keeping the last known values: {text}",
                             environment=self.environment)
            self.last_error = text
            return False
        if self.last_error is not None:
            jsonlog.emit("INFO", "Feature flags reachable again", environment=self.environment)
        self.features = features
        self.fetched_at = self._now()
        self.last_error = None
        return True

    def maybe_refresh(self) -> asyncio.Task | None:
        """Start a background refresh if the cache is older than 15 seconds. Never waits for it."""
        if not self.configured or (self._task is not None and not self._task.done()):
            return None
        if self._attempted is not None and self._monotonic() - self._attempted < self.refresh_seconds:
            return None
        self._attempted = self._monotonic()
        self._task = asyncio.get_running_loop().create_task(self.refresh())
        return self._task

    def source(self, name: str) -> str:
        if name in self.overrides:
            return "FLAGS_OVERRIDE (local override)"
        if self.configured:
            return f"GitLab feature flags ({self.environment})"
        return "default off (no flag service set)"

    def summary(self, name: str) -> str:
        if name in self.overrides:
            return "on for every user" if self.overrides[name] else "off"
        feature = self.features.get(name)
        if feature is None:
            return "off (not set for this environment)" if self.fetched_at else "off"
        if not feature["enabled"]:
            return "off"
        return " or ".join(describe_strategy(s) for s in feature["strategies"]) or "on for every user"

    def names(self) -> list[str]:
        return list(KNOWN_FLAGS) + sorted(set(self.overrides) - set(KNOWN_FLAGS))
