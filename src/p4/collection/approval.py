from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from p4.io.hashing import sha256_file


class ApprovalRequired(RuntimeError):
    pass


@dataclass(frozen=True)
class Approval:
    approval_id: str
    scope: str
    expires_at: datetime
    source_policy_sha256: str
    query_registry_sha256: str
    max_requests: int

    @classmethod
    def load(cls, path: Path) -> Approval:
        payload = json.loads(path.read_text(encoding="utf-8"))
        required = {
            "approvalId",
            "scope",
            "expiresAt",
            "sourcePolicySha256",
            "queryRegistrySha256",
            "maxRequests",
        }
        missing = required.difference(payload)
        if missing:
            raise ApprovalRequired(f"APPROVAL_INCOMPLETE: {sorted(missing)}")
        expires = datetime.fromisoformat(payload["expiresAt"].replace("Z", "+00:00"))
        if expires <= datetime.now(UTC):
            raise ApprovalRequired("APPROVAL_EXPIRED")
        return cls(
            approval_id=str(payload["approvalId"]),
            scope=str(payload["scope"]),
            expires_at=expires,
            source_policy_sha256=str(payload["sourcePolicySha256"]),
            query_registry_sha256=str(payload["queryRegistrySha256"]),
            max_requests=int(payload["maxRequests"]),
        )

    def validate_binding(self, policy: Path, registry: Path) -> None:
        if sha256_file(policy) != self.source_policy_sha256:
            raise ApprovalRequired("APPROVAL_SOURCE_POLICY_SHA_MISMATCH")
        if sha256_file(registry) != self.query_registry_sha256:
            raise ApprovalRequired("APPROVAL_QUERY_REGISTRY_SHA_MISMATCH")
        if self.max_requests < 1:
            raise ApprovalRequired("APPROVAL_REQUEST_BUDGET_INVALID")
