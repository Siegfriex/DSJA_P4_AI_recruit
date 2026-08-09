from __future__ import annotations

import hashlib
import hmac
import json
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from p4.io.hashing import sha256_file


class ApprovalRequired(RuntimeError):
    """Raised before transport when approval authority is incomplete or invalid."""


def canonical_approval_bytes(payload: dict) -> bytes:
    unsigned = {key: value for key, value in payload.items() if key != "signature"}
    return json.dumps(unsigned, sort_keys=True, separators=(",", ":")).encode()


def sign_approval(payload: dict, signing_key: bytes) -> str:
    return hmac.new(signing_key, canonical_approval_bytes(payload), hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class Approval:
    approval_id: str
    scope: str
    expires_at: datetime
    source_policy_sha256: str
    query_registry_sha256: str
    max_requests: int
    operations: frozenset[str]
    period_start: str
    period_end: str
    signed_by: str
    signature: str

    @classmethod
    def load(cls, path: Path, *, signing_key: bytes | None) -> Approval:
        if not signing_key:
            raise ApprovalRequired("APPROVAL_SIGNING_KEY_REQUIRED")
        payload = json.loads(path.read_text(encoding="utf-8"))
        required = {
            "approvalId",
            "scope",
            "expiresAt",
            "sourcePolicySha256",
            "queryRegistrySha256",
            "maxRequests",
            "operations",
            "periodStart",
            "periodEnd",
            "signedBy",
            "signatureAlgorithm",
            "signature",
        }
        missing = required.difference(payload)
        if missing:
            raise ApprovalRequired(f"APPROVAL_INCOMPLETE: {sorted(missing)}")
        if payload["signatureAlgorithm"] != "HMAC-SHA256":
            raise ApprovalRequired("APPROVAL_SIGNATURE_ALGORITHM_UNSUPPORTED")
        expected_signature = sign_approval(payload, signing_key)
        if not hmac.compare_digest(str(payload["signature"]), expected_signature):
            raise ApprovalRequired("APPROVAL_SIGNATURE_INVALID")
        expires = datetime.fromisoformat(str(payload["expiresAt"]).replace("Z", "+00:00"))
        if expires <= datetime.now(UTC):
            raise ApprovalRequired("APPROVAL_EXPIRED")
        operations = frozenset(str(value) for value in payload["operations"])
        if not operations:
            raise ApprovalRequired("APPROVAL_OPERATIONS_EMPTY")
        period_start = str(payload["periodStart"])
        period_end = str(payload["periodEnd"])
        if period_start > period_end:
            raise ApprovalRequired("APPROVAL_PERIOD_REVERSED")
        approval = cls(
            approval_id=str(payload["approvalId"]),
            scope=str(payload["scope"]),
            expires_at=expires,
            source_policy_sha256=str(payload["sourcePolicySha256"]),
            query_registry_sha256=str(payload["queryRegistrySha256"]),
            max_requests=int(payload["maxRequests"]),
            operations=operations,
            period_start=period_start,
            period_end=period_end,
            signed_by=str(payload["signedBy"]),
            signature=str(payload["signature"]),
        )
        if approval.max_requests < 1:
            raise ApprovalRequired("APPROVAL_REQUEST_BUDGET_INVALID")
        return approval

    def validate_binding(self, policy: Path, registry: Path) -> None:
        if sha256_file(policy) != self.source_policy_sha256:
            raise ApprovalRequired("APPROVAL_SOURCE_POLICY_SHA_MISMATCH")
        if sha256_file(registry) != self.query_registry_sha256:
            raise ApprovalRequired("APPROVAL_QUERY_REGISTRY_SHA_MISMATCH")

    def validate_request(self, *, operation: str, period: str) -> None:
        if datetime.now(UTC) >= self.expires_at:
            raise ApprovalRequired("APPROVAL_EXPIRED")
        if operation not in self.operations:
            raise ApprovalRequired("APPROVAL_OPERATION_OUT_OF_SCOPE")
        if not self.period_start <= period <= self.period_end:
            raise ApprovalRequired("APPROVAL_PERIOD_OUT_OF_SCOPE")


class RequestBudget:
    def __init__(self, maximum: int) -> None:
        if maximum < 1:
            raise ValueError("request budget must be positive")
        self.maximum = maximum
        self._used = 0
        self._lock = threading.Lock()

    @property
    def used(self) -> int:
        with self._lock:
            return self._used

    def reserve(self) -> int:
        with self._lock:
            if self._used >= self.maximum:
                raise ApprovalRequired("APPROVAL_REQUEST_BUDGET_EXHAUSTED")
            self._used += 1
            return self._used


@dataclass
class ApprovedRequestContext:
    approval: Approval
    budget: RequestBudget
    operation: str
    period: str

    def before_transport(self) -> None:
        self.approval.validate_request(operation=self.operation, period=self.period)
        self.budget.reserve()
