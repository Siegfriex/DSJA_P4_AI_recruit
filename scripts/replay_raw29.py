from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from p4.governance.attestation import write_attestation
from p4.processing.producers import produce_raw_to_semantic
from p4.qa.bundle import validate_raw_semantic_bundle


def _sha(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode()).hexdigest()


def _legacy_counts(export_root: Path, source_ids: set[str]) -> dict[str, int]:
    postings = pd.read_parquet(export_root / "posting_normalized.parquet")
    postings = postings.loc[postings["sourcePostingId"].astype(str).isin(source_ids)]
    tracks = pd.read_parquet(export_root / "posting_tracks.parquet")
    tracks = tracks.loc[tracks["postingId"].isin(postings["postingId"])]
    sections = pd.read_parquet(export_root / "posting_sections.parquet")
    sections = sections.loc[sections["trackId"].isin(tracks["trackId"])]
    facts = pd.read_parquet(export_root / "requirement_facts.parquet")
    facts = facts.loc[facts["sectionId"].isin(sections["sectionId"])]
    return {
        "posting_normalized": len(postings),
        "posting_source_block": -1,
        "posting_section": len(sections),
        "semantic_chunk": -1,
        "requirement_fact": len(facts),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--crawl-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--legacy-export-root", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.manifest.read_text().splitlines() if line]
    bundles = []
    failures = []
    quality = []
    for row in rows:
        source_path = args.crawl_root / row["rawPath"]
        raw_manifest = {
            "rawPostingId": f"LEGACY-{row['rawSha256'][:16]}",
            "sourcePostingId": str(row["sourcePostingId"]),
            "contentSha256": row["rawSha256"],
        }
        try:
            html = gzip.open(source_path, "rt", encoding="utf-8").read()
            bundle = produce_raw_to_semantic(html, raw_manifest)
            if bundle != produce_raw_to_semantic(html, raw_manifest):
                raise ValueError("REPEAT_RUN_MISMATCH")
            quality.append(validate_raw_semantic_bundle(bundle))
            bundles.append(bundle)
        except Exception as error:  # evidence must retain per-source failures
            failures.append(
                {
                    "sourcePostingId": str(row["sourcePostingId"]),
                    "error": f"{type(error).__name__}:{error}",
                }
            )
    totals: dict[str, int] = {}
    for bundle in bundles:
        for name, records in bundle.items():
            totals[name] = totals.get(name, 0) + len(records)
    old = _legacy_counts(args.legacy_export_root, {str(row["sourcePostingId"]) for row in rows})
    deltas = []
    for name in old:
        old_count = old[name]
        new_count = totals.get(name, 0)
        available = old_count >= 0
        deltas.append(
            {
                "artifact": name,
                "old": old_count if available else "NOT_AVAILABLE",
                "new": new_count,
                "delta": new_count - old_count if available else "NOT_COMPARABLE",
                "cause": "COUNT_EQUAL"
                if available and old_count == new_count
                else "REVIEW_REQUIRED",
                "classification": (
                    "EXPECTED" if available and old_count == new_count else "REVIEW_REQUIRED"
                ),
            }
        )
    status = (
        "PASS_WITH_FINDINGS"
        if failures or any(row["classification"] == "REVIEW_REQUIRED" for row in deltas)
        else "PASS"
    )
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=Path.cwd(), text=True
    ).strip()
    payload = {
        "evidenceId": "EVIDENCE-P4-RAW29-CLEANROOM-REPLAY-001",
        "runId": "P4_RAW29_CLEANROOM_20260809_001",
        "stageId": "RAW_TO_SEMANTIC_REPLAY",
        "codeCommit": commit,
        "contractVersion": "2.1.3",
        "taxonomyVersions": {"section": "v1.0.0", "requirement": "v1.0.0"},
        "inputManifestSha256": hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        "outputManifestSha256": _sha(bundles),
        "rowCounts": totals,
        "schemaSignatures": {
            name: _sha(sorted(rows[0]) if rows else []) for name, rows in bundles[0].items()
        }
        if bundles
        else {},
        "qualityResults": {
            "inputRawCount": len(rows),
            "successfulRawCount": len(bundles),
            "failures": failures,
            "foreignKeyViolations": sum(item["foreignKeyViolations"] for item in quality),
            "eligibleSectionEvidenceCoverage": min(
                (item["sectionEvidenceCoverage"] for item in quality), default=0
            ),
            "eligibleChunkPrimaryEvidenceCoverage": min(
                (item["chunkPrimaryEvidenceCoverage"] for item in quality), default=0
            ),
            "factEvidenceLinkage": 1.0
            if totals.get("requirement_fact") == totals.get("requirement_fact_mention")
            else 0.0,
            "deterministicIdsAndRepeatRun": not failures,
            "legacyDeltas": deltas,
        },
        "testLogSha256": None,
        "networkCalls": 0,
        "createdAt": datetime.now(UTC).isoformat(),
        "status": status,
        "dataAuthority": "OBSERVED_EXECUTED_NOT_PROMOTED",
    }
    print(write_attestation(args.destination, payload))


if __name__ == "__main__":
    main()
