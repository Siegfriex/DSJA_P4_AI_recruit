from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from p4.collection.approval import Approval, ApprovalRequired, RequestBudget, sign_approval


def approval_payload() -> dict:
    return {
        "approvalId": "A1",
        "scope": "FIXTURE",
        "expiresAt": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        "sourcePolicySha256": "a" * 64,
        "queryRegistrySha256": "b" * 64,
        "maxRequests": 1,
        "operations": ["DetailPage"],
        "periodStart": "2026-01",
        "periodEnd": "2026-01",
        "signedBy": "TEST",
        "signatureAlgorithm": "HMAC-SHA256",
    }


def test_signature_scope_period_and_budget_fail_closed(tmp_path) -> None:
    key = b"test-key"
    payload = approval_payload()
    payload["signature"] = sign_approval(payload, key)
    path = tmp_path / "approval.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    approval = Approval.load(path, signing_key=key)
    approval.validate_request(operation="DetailPage", period="2026-01")
    with pytest.raises(ApprovalRequired, match="OPERATION_OUT_OF_SCOPE"):
        approval.validate_request(operation="AssetFetch", period="2026-01")
    with pytest.raises(ApprovalRequired, match="PERIOD_OUT_OF_SCOPE"):
        approval.validate_request(operation="DetailPage", period="2026-02")
    budget = RequestBudget(1)
    assert budget.reserve() == 1
    with pytest.raises(ApprovalRequired, match="BUDGET_EXHAUSTED"):
        budget.reserve()


def test_tampered_approval_signature_is_rejected(tmp_path) -> None:
    key = b"test-key"
    payload = approval_payload()
    payload["signature"] = sign_approval(payload, key)
    payload["maxRequests"] = 999
    path = tmp_path / "approval.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ApprovalRequired, match="SIGNATURE_INVALID"):
        Approval.load(path, signing_key=key)
