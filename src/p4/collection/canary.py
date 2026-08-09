from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanaryPlan:
    tier: int
    scope: str
    max_index_requests: int = 0
    max_detail_requests: int = 0
    max_asset_requests: int = 0

    def validate(self) -> None:
        if self.tier == 0 and any(
            (self.max_index_requests, self.max_detail_requests, self.max_asset_requests)
        ):
            raise ValueError("TIER0_MUST_HAVE_ZERO_TRANSPORT")
        if (
            self.max_index_requests > 28
            or self.max_detail_requests > 10
            or self.max_asset_requests > 30
        ):
            raise ValueError("CANARY_BUDGET_EXCEEDED")
