from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from p4.docs.hashing import sha256_path

REQUIRED_FIELDS = {
    "evidenceId",
    "runId",
    "stageId",
    "codeCommit",
    "contractVersion",
    "taxonomyVersions",
    "inputManifestSha256",
    "outputManifestSha256",
    "rowCounts",
    "schemaSignatures",
    "qualityResults",
    "testLogSha256",
    "networkCalls",
    "createdAt",
    "status",
}


def write_attestation(destination: Path, payload: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_FIELDS.difference(payload)
    if missing:
        raise ValueError(f"ATTESTATION_FIELDS_MISSING:{sorted(missing)}")
    if payload["status"] == "CANONICAL_PROMOTED":
        raise ValueError("AUTOMATIC_CANONICAL_PROMOTION_FORBIDDEN")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )
    return {"path": destination.as_posix(), "sha256": sha256_path(destination)}
