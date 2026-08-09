from __future__ import annotations


def validate_raw_semantic_bundle(bundle: dict[str, list[dict]]) -> dict:
    def ids(table: str, key: str) -> set[str]:
        values = [str(row[key]) for row in bundle[table]]
        if len(values) != len(set(values)):
            raise ValueError(f"DUPLICATE_PRIMARY_KEY:{table}.{key}")
        return set(values)

    posting_ids = ids("posting_normalized", "postingId")
    block_ids = ids("posting_source_block", "sourceBlockId")
    track_ids = ids("posting_track", "trackId")
    section_ids = ids("posting_section", "sectionId")
    chunk_ids = ids("semantic_chunk", "chunkId")
    mention_ids = ids("requirement_mention", "mentionId")
    fact_ids = ids("requirement_fact", "requirementFactId")
    violations: list[str] = []

    def require_subset(values: set[str], parents: set[str], name: str) -> None:
        if values - parents:
            violations.append(name)

    require_subset(
        {str(row["postingId"]) for row in bundle["posting_source_block"]},
        posting_ids,
        "block_to_posting",
    )
    require_subset(
        {str(row["postingId"]) for row in bundle["posting_track"]}, posting_ids, "track_to_posting"
    )
    require_subset(
        {str(row["trackId"]) for row in bundle["posting_section"]}, track_ids, "section_to_track"
    )
    require_subset(
        {str(row["sectionId"]) for row in bundle["section_source_block"]},
        section_ids,
        "section_bridge_to_section",
    )
    require_subset(
        {str(row["sourceBlockId"]) for row in bundle["section_source_block"]},
        block_ids,
        "section_bridge_to_block",
    )
    require_subset(
        {str(row["sectionId"]) for row in bundle["semantic_chunk"]},
        section_ids,
        "chunk_to_section",
    )
    require_subset(
        {str(row["chunkId"]) for row in bundle["chunk_source_block"]},
        chunk_ids,
        "chunk_bridge_to_chunk",
    )
    require_subset(
        {str(row["sourceBlockId"]) for row in bundle["chunk_source_block"]},
        block_ids,
        "chunk_bridge_to_block",
    )
    require_subset(
        {str(row["chunkId"]) for row in bundle["requirement_mention"]},
        chunk_ids,
        "mention_to_chunk",
    )
    require_subset(
        {str(row["mentionId"]) for row in bundle["requirement_fact_mention"]},
        mention_ids,
        "fact_bridge_to_mention",
    )
    require_subset(
        {str(row["requirementFactId"]) for row in bundle["requirement_fact_mention"]},
        fact_ids,
        "fact_bridge_to_fact",
    )
    if violations:
        raise ValueError(f"FOREIGN_KEY_VIOLATIONS:{sorted(violations)}")
    section_with_evidence = {str(row["sectionId"]) for row in bundle["section_source_block"]}
    chunk_with_primary = {
        str(row["chunkId"])
        for row in bundle["chunk_source_block"]
        if row["evidenceRole"] == "PRIMARY"
    }
    section_coverage = len(section_with_evidence) / len(section_ids) if section_ids else 1.0
    chunk_coverage = len(chunk_with_primary) / len(chunk_ids) if chunk_ids else 1.0
    source_modes = {row["sourceMode"] for row in bundle["posting_source_block"]}
    if not source_modes <= {"HTML", "ACTIVITY_TEXT", "OCR"}:
        raise ValueError("INVALID_SOURCE_MODE")
    status = "PASS" if section_coverage == chunk_coverage == 1.0 else "FAIL"
    return {
        "status": status,
        "foreignKeyViolations": 0,
        "sectionEvidenceCoverage": section_coverage,
        "chunkPrimaryEvidenceCoverage": chunk_coverage,
        "rowCounts": {name: len(rows) for name, rows in bundle.items()},
    }
