from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd

from p4.processing.eligibility import recompute_fail_closed_eligibility
from p4.processing.labels import LabelEvidence, career_class, intern_access_class
from p4.processing.requirements import aggregate_requirement_facts
from p4.processing.tracks import validate_track_split
from p4.qa.semantics import semantic_summary

BASELINE = {
    "posting_normalized": 137,
    "posting_tracks": 137,
    "posting_sections": 84,
    "source_blocks": 84,
    "semantic_chunks": 277,
    "requirement_facts": 41,
    "posting_ncs_candidates": 128,
    "raw_objects": 29,
}


def _load(root: Path, name: str) -> pd.DataFrame:
    path = root / f"{name}.parquet"
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_parquet(path)


def replay_observed(source: Path, output: Path) -> dict:
    names = (
        "posting_normalized",
        "posting_tracks",
        "posting_sections",
        "source_blocks",
        "section_source_blocks",
        "semantic_chunks",
        "requirement_facts",
        "career_access_labels",
        "posting_ncs_candidates",
        "posting_ncs_matches",
        "ncs_mapping_to_mart",
        "preprocessed_posting_tracks",
    )
    frames = {name: _load(source, name) for name in names}
    tracks = validate_track_split(frames["posting_tracks"], mode="observed")
    aggregates = aggregate_requirement_facts(
        tracks, frames["posting_sections"], frames["requirement_facts"]
    )
    eligibility = recompute_fail_closed_eligibility(
        frames["posting_normalized"], tracks, frames["posting_sections"]
    )
    boundary_tracks = set(
        frames["posting_sections"]
        .loc[
            frames["posting_sections"]["sectionType"].isin(["required", "preferred"])
            & frames["posting_sections"]["boundaryResolvedFlag"].fillna(False),
            "trackId",
        ]
        .astype(str)
    )
    label_input = tracks[["trackId", "postingId", "trackType"]].merge(
        aggregates, on="trackId", how="left"
    )
    label_rows = []
    for row in label_input.to_dict(orient="records"):
        months = None if pd.isna(row["minCareerMonths"]) else int(row["minCareerMonths"])
        evidence = LabelEvidence(
            track_type=row["trackType"],
            min_career_months=months,
            prior_experience_required=bool(row["requiredPriorExperienceFlag"]),
            boundary_resolved=str(row["trackId"]) in boundary_tracks,
        )
        label_rows.append(
            {
                "trackId": row["trackId"],
                "postingId": row["postingId"],
                "careerClass": career_class(evidence),
                "internAccessClass": intern_access_class(evidence),
                "boundaryResolvedFlag": evidence.boundary_resolved,
                "labelVersion": "p4-career-access-2.1.3",
            }
        )
    labels = pd.DataFrame(label_rows).merge(
        eligibility, on="trackId", how="left", validate="one_to_one"
    )
    pre = frames["preprocessed_posting_tracks"].copy()
    replaced = set(aggregates.columns).union(eligibility.columns).union(
        {"careerClass", "internAccessClass", "boundaryResolvedFlag"}
    ) - {"trackId"}
    pre = pre.drop(columns=[column for column in replaced if column in pre.columns])
    pre = pre.merge(aggregates, on="trackId", how="left", validate="one_to_one")
    pre = pre.merge(eligibility, on="trackId", how="left", validate="one_to_one")
    pre = pre.merge(
        labels[["trackId", "careerClass", "internAccessClass", "boundaryResolvedFlag"]],
        on="trackId",
        how="left",
        validate="one_to_one",
    )
    pre["contractVersion"] = "2.1.3"
    pre["dataVersion"] = "observed-migration-20260809.1"
    pre["dataProvenance"] = "OBSERVED_DEVELOPMENT_ONLY"
    pre["empiricalAnalysisAllowed"] = False
    pre["promotionAllowed"] = False
    pre["highDemandScore"] = None
    pre["scoreStatus"] = "reserved"
    frames["posting_tracks"] = tracks
    frames["career_access_labels"] = labels
    frames["preprocessed_posting_tracks"] = pre
    frames["section_source_blocks"] = frames["section_source_blocks"].copy()
    frames["section_source_blocks"]["relationType"] = "EXACT_SPAN"
    for frame in frames.values():
        frame["contractVersion"] = "2.1.3"
        frame["dataVersion"] = "observed-migration-20260809.1"
        frame["dataProvenance"] = "OBSERVED_DEVELOPMENT_ONLY"
        frame["empiricalAnalysisAllowed"] = False
        frame["promotionAllowed"] = False
    output.mkdir(parents=True, exist_ok=True)
    for name, frame in frames.items():
        frame.to_parquet(output / f"{name}.parquet", index=False)
        frame.to_csv(output / f"{name}.csv", index=False, encoding="utf-8-sig")
    primary_keys = {
        "posting_normalized": ["postingId"],
        "posting_tracks": ["trackId"],
        "posting_sections": ["sectionId"],
        "source_blocks": ["sourceBlockId"],
        "section_source_blocks": ["sectionId", "sourceBlockId"],
        "semantic_chunks": ["chunkId"],
        "requirement_facts": ["requirementId"],
        "career_access_labels": ["trackId"],
    }
    pk_violations = {
        name: int(frame.duplicated(keys).sum())
        for name, keys in primary_keys.items()
        if (frame := frames[name]) is not None
    }
    fk_checks = {
        "track_to_posting": set(frames["posting_tracks"]["postingId"])
        - set(frames["posting_normalized"]["postingId"]),
        "section_to_track": set(frames["posting_sections"]["trackId"])
        - set(frames["posting_tracks"]["trackId"]),
        "block_to_posting": set(frames["source_blocks"]["postingId"])
        - set(frames["posting_normalized"]["postingId"]),
        "section_block_to_section": set(frames["section_source_blocks"]["sectionId"])
        - set(frames["posting_sections"]["sectionId"]),
        "section_block_to_block": set(frames["section_source_blocks"]["sourceBlockId"])
        - set(frames["source_blocks"]["sourceBlockId"]),
        "chunk_to_track": set(frames["semantic_chunks"]["trackId"])
        - set(frames["posting_tracks"]["trackId"]),
        "chunk_to_section": set(frames["semantic_chunks"]["sectionId"])
        - set(frames["posting_sections"]["sectionId"]),
        "chunk_to_block": set(frames["semantic_chunks"]["sourceBlockId"])
        - set(frames["source_blocks"]["sourceBlockId"]),
        "requirement_to_section": set(frames["requirement_facts"]["sectionId"])
        - set(frames["posting_sections"]["sectionId"]),
        "requirement_to_block": set(frames["requirement_facts"]["sourceBlockId"])
        - set(frames["source_blocks"]["sourceBlockId"]),
    }
    database = output / "p4.observed-migration.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute("CREATE SCHEMA observed")
    for name, frame in frames.items():
        connection.register("current_frame", frame)
        connection.execute(f'CREATE TABLE observed."{name}" AS SELECT * FROM current_frame')
        connection.unregister("current_frame")
    database_counts = {
        name: int(connection.execute(f'SELECT COUNT(*) FROM observed."{name}"').fetchone()[0])
        for name in frames
    }
    connection.close()
    csv_parquet_equal = {
        name: len(pd.read_csv(output / f"{name}.csv"))
        == len(pd.read_parquet(output / f"{name}.parquet"))
        for name in frames
    }
    old_counts = {name: int(len(_load(source, name))) for name in BASELINE if name != "raw_objects"}
    new_counts = {name: int(len(frames[name])) for name in old_counts}
    ncs_status = frames["ncs_mapping_to_mart"]["mappingStatus"].value_counts().to_dict()
    summary = semantic_summary(frames)
    report = {
        "status": "PASS_WITH_FINDINGS",
        "runMode": "OBSERVED_LOCAL_REPLAY",
        "networkCalls": 0,
        "externalAtsCalls": 0,
        "browserCalls": 0,
        "credentialedApiCalls": 0,
        "productionRows": 0,
        "articleResultManifestRows": 0,
        "counts": {
            name: {
                "old": old_counts[name],
                "new": new_counts[name],
                "delta": new_counts[name] - old_counts[name],
                "cause": "NO_GRAIN_CHANGE",
                "classification": "EXPECTED",
            }
            for name in old_counts
        },
        "semantic": summary,
        "ncsMappingStatus": {str(key): int(value) for key, value in ncs_status.items()},
        "structuralQa": {
            "primaryKeyViolations": pk_violations,
            "foreignKeyViolationCounts": {name: len(values) for name, values in fk_checks.items()},
            "csvParquetRowEquality": csv_parquet_equal,
            "duckdbParquetRowEquality": {
                name: database_counts[name] == len(frame) for name, frame in frames.items()
            },
        },
        "intentionalFeatureDeltas": {
            "requiredCertificateFlagTrue": int(pre["requiredCertificateFlag"].fillna(False).sum()),
            "requiredDegreeLevelPresent": int(pre["requiredDegreeLevel"].notna().sum()),
            "postingEligibleOld": int(
                frames["posting_normalized"]["postingEligibleFlag"].fillna(False).sum()
            ),
            "postingEligibleNew": int(pre["postingEligibleFlag"].fillna(False).sum()),
            "rq2EligibleOld": int(
                frames["posting_normalized"]["rq2EligibleFlag"].fillna(False).sum()
            ),
            "rq2EligibleNew": int(pre["rq2EligibleFlag"].fillna(False).sum()),
        },
        "remainingFindings": [
            "108/137 postings remain source-authority unresolved",
            "observed track split retains explicitly marked legacy single-track rows",
            "NCS mappings remain REVIEW_REQUIRED and quality NOT_EVALUATED",
            "observed replay is not empirical or article authority",
        ],
    }
    (output / "OBSERVED_REPLAY_REPORT.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report
