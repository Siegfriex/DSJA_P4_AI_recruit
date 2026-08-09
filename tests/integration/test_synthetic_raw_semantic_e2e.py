from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd

from p4.collection.approval import Approval, sign_approval
from p4.collection.assets import hosted_asset_candidates
from p4.collection.runner import CollectionRunner
from p4.io.hashing import sha256_file
from p4.ncs.retrieval import lexical_candidates
from p4.processing.producers import produce_raw_to_semantic, stable_id
from p4.qa.bundle import validate_raw_semantic_bundle

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures"


@dataclass
class Response:
    status_code: int
    content: bytes


def test_mock_apq_to_ncs_candidate_is_deterministic_and_fully_linked(tmp_path: Path) -> None:
    index_bytes = (FIXTURES / "index_response.json").read_bytes()
    detail_bytes = (FIXTURES / "detail_page.html").read_bytes()

    def transport(url: str, **_kwargs) -> Response:
        if url.endswith("/api/graphql"):
            return Response(200, index_bytes)
        if url.endswith("/activity/1001"):
            return Response(200, detail_bytes)
        raise AssertionError(f"unexpected fixture URL: {url}")

    key = b"fixture-only-signing-key"
    approval_payload = {
        "approvalId": "FIXTURE-T0-001",
        "scope": "SYNTHETIC_FIXTURE_ONLY",
        "expiresAt": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        "sourcePolicySha256": sha256_file(ROOT / "config/source_policy.yaml"),
        "queryRegistrySha256": sha256_file(ROOT / "config/query_registry.yaml"),
        "maxRequests": 2,
        "operations": ["CalendarScreen_Activities", "DetailPage"],
        "periodStart": "2026-01",
        "periodEnd": "2026-01",
        "signedBy": "FIXTURE_TEST",
        "signatureAlgorithm": "HMAC-SHA256",
    }
    approval_payload["signature"] = sign_approval(approval_payload, key)
    approval_path = tmp_path / "approval.json"
    approval_path.write_text(json.dumps(approval_payload), encoding="utf-8")
    approval = Approval.load(approval_path, signing_key=key)
    runner = CollectionRunner(
        transport=transport,
        approval=approval,
        policy_path=ROOT / "config/source_policy.yaml",
        registry_path=ROOT / "config/query_registry.yaml",
        raw_root=tmp_path / "raw",
    )

    discovered = runner.discover(period="2026-01", url="https://linkareer.com/api/graphql")
    assert discovered == ["1001"]
    raw_manifest = runner.fetch_detail(
        period="2026-01",
        source_posting_id="1001",
        url="https://linkareer.com/activity/1001",
    )
    raw_path = tmp_path / "raw" / raw_manifest["objectLocatorRelative"]
    html = gzip.decompress(raw_path.read_bytes()).decode()
    first = produce_raw_to_semantic(html, raw_manifest)
    second = produce_raw_to_semantic(html, raw_manifest)
    assert first == second
    qa = validate_raw_semantic_bundle(first)
    assert qa["status"] == "PASS"
    assert qa["foreignKeyViolations"] == 0
    assert qa["sectionEvidenceCoverage"] == 1.0
    assert qa["chunkPrimaryEvidenceCoverage"] == 1.0

    corpus = pd.read_csv(FIXTURES / "ncs_units_small.csv")
    duty_chunk = next(row for row in first["semantic_chunk"] if row["chunkRole"] == "DUTY")
    candidates = lexical_candidates(duty_chunk["chunkText"], corpus, "text", top_k=2)
    candidate_rows = [
        {
            "candidateId": stable_id(
                "NCS-CAND", "FIXTURE-RUN", duty_chunk["chunkId"], row.ncsUnitCode
            ),
            "candidateRunId": "FIXTURE-RUN",
            "chunkId": duty_chunk["chunkId"],
            "ncsUnitCode": row.ncsUnitCode,
            "score": row.score,
            "status": "CANDIDATE_NOT_REFERENCE",
        }
        for row in candidates.itertuples()
    ]
    assert candidate_rows[0]["ncsUnitCode"] == "NCS-DATA-01"
    assert len({row["candidateId"] for row in candidate_rows}) == len(candidate_rows)
    assert runner.state.network_calls == 2
    assert runner.budget.used == 2

    assets = json.loads((FIXTURES / "asset_metadata.json").read_text())["assets"]
    hosted = hosted_asset_candidates(
        "https://linkareer.com/activity/1001", [item["url"] for item in assets]
    )
    assert hosted == ["https://linkareer.com/assets/synthetic-1001.png"]
