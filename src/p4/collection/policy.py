from __future__ import annotations

import random
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse


class SourcePolicyBlocked(RuntimeError):
    """Raised before or during transport when a safety boundary is violated."""


class ResponseLike(Protocol):
    status_code: int
    content: bytes


@dataclass(frozen=True)
class SourcePolicyConfig:
    requests_per_second: float = 1.0
    max_concurrency: int = 2
    max_retries: int = 3
    max_consecutive_403: int = 1
    max_consecutive_429: int = 3
    minimum_success_rate: float = 0.80
    success_window: int = 20
    minimum_success_samples: int = 5

    def __post_init__(self) -> None:
        if not 0 < self.requests_per_second <= 1:
            raise ValueError("requests_per_second must be in (0, 1]")
        if not 1 <= self.max_concurrency <= 2:
            raise ValueError("max_concurrency must be in [1, 2]")
        if self.max_retries != 3:
            raise ValueError("the canonical policy requires exactly three retries")
        if min(self.max_consecutive_403, self.max_consecutive_429) < 1:
            raise ValueError("kill-switch thresholds must be positive")


def is_allowed_linkareer_url(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    return parsed.scheme == "https" and (host == "linkareer.com" or host.endswith(".linkareer.com"))


class SourceHealthMonitor:
    def __init__(self, config: SourcePolicyConfig) -> None:
        self.config = config
        self.consecutive_403 = 0
        self.consecutive_429 = 0
        self.outcomes: deque[bool] = deque(maxlen=config.success_window)

    def observe(self, status_code: int) -> None:
        self.outcomes.append(200 <= status_code < 400)
        self.consecutive_403 = self.consecutive_403 + 1 if status_code == 403 else 0
        self.consecutive_429 = self.consecutive_429 + 1 if status_code == 429 else 0
        if self.consecutive_403 >= self.config.max_consecutive_403:
            raise SourcePolicyBlocked("SOURCE_POLICY_BLOCKED: MAX_CONSECUTIVE_403")
        if self.consecutive_429 >= self.config.max_consecutive_429:
            raise SourcePolicyBlocked("SOURCE_POLICY_BLOCKED: MAX_CONSECUTIVE_429")
        if len(self.outcomes) >= self.config.minimum_success_samples:
            rate = sum(self.outcomes) / len(self.outcomes)
            if rate < self.config.minimum_success_rate:
                raise SourcePolicyBlocked("SOURCE_POLICY_BLOCKED: MINIMUM_SUCCESS_RATE")


@dataclass
class PolicyHttpClient:
    transport: Callable[..., ResponseLike]
    config: SourcePolicyConfig = SourcePolicyConfig()
    sleeper: Callable[[float], None] = time.sleep
    random_uniform: Callable[[float, float], float] = random.uniform
    before_transport: Callable[[], None] | None = None

    def __post_init__(self) -> None:
        self._lock = threading.Lock()
        self._semaphore = threading.BoundedSemaphore(self.config.max_concurrency)
        self._last_start: float | None = None
        self.health = SourceHealthMonitor(self.config)

    def _rate_limit(self) -> None:
        with self._lock:
            now = time.monotonic()
            if self._last_start is not None:
                delay = (1 / self.config.requests_per_second) - (now - self._last_start)
                if delay > 0:
                    self.sleeper(delay)
            self._last_start = time.monotonic()

    def get(self, url: str, **kwargs) -> ResponseLike:
        if not is_allowed_linkareer_url(url):
            raise SourcePolicyBlocked("EXTERNAL_ATS_TRANSPORT_REJECTED")
        for attempt in range(self.config.max_retries + 1):
            self._rate_limit()
            if self.before_transport is not None:
                self.before_transport()
            with self._semaphore:
                response = self.transport(url, **kwargs)
            self.health.observe(response.status_code)
            if (
                response.status_code in {429, 500, 502, 503, 504}
                and attempt < self.config.max_retries
            ):
                self.sleeper((2**attempt) + self.random_uniform(0.0, 0.25))
                continue
            body_prefix = response.content[:200_000].lower()
            if any(value in body_prefix for value in (b"access denied", b"captcha", b"datadome")):
                raise SourcePolicyBlocked("SOURCE_POLICY_BLOCKED: CHALLENGE_MARKER")
            return response
        raise AssertionError("unreachable retry state")
