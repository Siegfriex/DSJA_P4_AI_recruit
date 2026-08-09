from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from p4.collection.approval import Approval, ApprovedRequestContext, RequestBudget
from p4.collection.policy import PolicyHttpClient, SourcePolicyConfig
from p4.collection.recorder import record_response
from p4.io.hashing import sha256_text


@dataclass
class CollectionState:
    discovered_ids: set[str] = field(default_factory=set)
    detail_status: dict[str, str] = field(default_factory=dict)
    network_calls: int = 0


class CollectionRunner:
    """Approval-bound index/detail runner. Production adapters supply the transport."""

    def __init__(
        self,
        *,
        transport,
        approval: Approval,
        policy_path: Path,
        registry_path: Path,
        raw_root: Path,
        config: SourcePolicyConfig | None = None,
        sleeper=lambda _: None,
    ) -> None:
        approval.validate_binding(policy_path, registry_path)
        self.transport = transport
        self.approval = approval
        self.budget = RequestBudget(approval.max_requests)
        self.raw_root = raw_root
        self.config = config or SourcePolicyConfig()
        self.sleeper = sleeper
        self.state = CollectionState()

    def _client(self, *, operation: str, period: str) -> PolicyHttpClient:
        context = ApprovedRequestContext(self.approval, self.budget, operation, period)

        def counted_transport(url: str, **kwargs):
            self.state.network_calls += 1
            return self.transport(url, **kwargs)

        return PolicyHttpClient(
            counted_transport,
            config=self.config,
            sleeper=self.sleeper,
            random_uniform=lambda _left, _right: 0.0,
            before_transport=context.before_transport,
        )

    def discover(self, *, period: str, url: str) -> list[str]:
        operation = "CalendarScreen_Activities"
        response = self._client(operation=operation, period=period).get(
            url, params={"operationName": operation, "period": period}
        )
        payload = json.loads(response.content)
        nodes: list[dict[str, Any]] = payload["data"]["activities"]["nodes"]
        for node in nodes:
            self.state.discovered_ids.add(str(node["id"]))
        return sorted(self.state.discovered_ids)

    def fetch_detail(self, *, period: str, source_posting_id: str, url: str) -> dict:
        operation = "DetailPage"
        response = self._client(operation=operation, period=period).get(url)
        content_sha = sha256_text(response.content.decode("utf-8"))
        raw_posting_id = f"RAW-{source_posting_id}-{content_sha[:16]}"
        destination = self.raw_root / period / f"{content_sha}.html.gz"
        metadata = self.raw_root / period / f"{content_sha}.manifest.json"
        row = record_response(
            response.content,
            destination,
            metadata,
            url,
            raw_posting_id=raw_posting_id,
            source_posting_id=source_posting_id,
            operation=operation,
            period=period,
            storage_root=self.raw_root,
        )
        self.state.detail_status[source_posting_id] = "FETCHED"
        return row
