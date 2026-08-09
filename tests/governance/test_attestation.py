from __future__ import annotations

import pytest

from p4.governance.attestation import write_attestation


def test_attestation_cannot_auto_promote(tmp_path) -> None:
    payload = {
        "evidenceId": "E",
        "runId": "R",
        "stageId": "S",
        "codeCommit": "abc",
        "contractVersion": "2.1.3",
        "taxonomyVersions": {},
        "inputManifestSha256": "a",
        "outputManifestSha256": "b",
        "rowCounts": {},
        "schemaSignatures": {},
        "qualityResults": {},
        "testLogSha256": "c",
        "networkCalls": 0,
        "createdAt": "2026-08-09T00:00:00Z",
        "status": "CANONICAL_PROMOTED",
    }
    with pytest.raises(ValueError, match="AUTOMATIC_CANONICAL_PROMOTION_FORBIDDEN"):
        write_attestation(tmp_path / "attestation.yaml", payload)
