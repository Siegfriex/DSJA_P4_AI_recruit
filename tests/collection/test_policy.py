from __future__ import annotations

from dataclasses import dataclass

import pytest

from p4.collection.policy import PolicyHttpClient, SourcePolicyBlocked, SourcePolicyConfig


@dataclass
class Response:
    status_code: int
    content: bytes = b"ok"


def test_external_ats_is_rejected_before_transport() -> None:
    called = False

    def transport(url: str) -> Response:
        nonlocal called
        called = True
        return Response(200)

    client = PolicyHttpClient(transport, sleeper=lambda _: None)
    with pytest.raises(SourcePolicyBlocked, match="EXTERNAL_ATS"):
        client.get("https://example-ats.com/job/1")
    assert called is False


def test_retry_uses_four_total_attempts_and_backoff() -> None:
    statuses = iter([500, 502, 503, 200])
    sleeps = []
    client = PolicyHttpClient(
        lambda url: Response(next(statuses)),
        config=SourcePolicyConfig(minimum_success_samples=10),
        sleeper=sleeps.append,
        random_uniform=lambda left, right: 0.0,
    )
    response = client.get("https://linkareer.com/api/test")
    assert response.status_code == 200
    assert [value for value in sleeps if value in {1, 2, 4}] == [1, 2, 4]


def test_three_consecutive_429_trips_kill_switch() -> None:
    client = PolicyHttpClient(
        lambda url: Response(429),
        config=SourcePolicyConfig(minimum_success_samples=10),
        sleeper=lambda _: None,
    )
    with pytest.raises(SourcePolicyBlocked, match="429"):
        client.get("https://linkareer.com/api/test")
