from __future__ import annotations

TRACE_EDGES = (
    ("RQ-001", "METRIC-RQ1-ENTRY", "MEASURED_BY", "ACTIVE"),
    ("RQ-001", "MART-RQ1-GLOBAL", "COMPUTED_IN", "ACTIVE"),
    ("RQ-002A", "METRIC-RQ2A-PATH", "MEASURED_BY", "ACTIVE"),
    ("RQ-002A", "MART-RQ2A-MONTHLY", "COMPUTED_IN", "ACTIVE"),
    ("RQ-002B", "MART-NCS-BAND-MAIN", "COMPUTED_IN", "ACTIVE"),
    ("DATA-LKA-001", "PIPE-001", "INGESTED_BY", "ACTIVE"),
    ("PIPE-001", "raw_posting_version", "PRODUCES", "IMPLEMENTED"),
    ("raw_posting_version", "PIPE-002", "INGESTED_BY", "IMPLEMENTED"),
    ("PIPE-002", "posting_source_block", "PRODUCES", "IMPLEMENTED"),
    ("PIPE-002", "semantic_chunk", "PRODUCES", "IMPLEMENTED"),
    ("semantic_chunk", "PIPE-003", "FEEDS", "IMPLEMENTED"),
    ("TAXONOMY-REQUIREMENT", "requirement_fact", "NORMALIZES", "IMPLEMENTED"),
    ("requirement_fact", "MART-RQ2A-MONTHLY", "FEEDS", "FUTURE"),
    ("DATA-NCS-001", "PIPE-004", "REFERENCED_BY", "FUTURE"),
    ("PIPE-004", "ncs_candidate", "PRODUCES", "IMPLEMENTED_BASELINE"),
    ("ncs_mapping_reference", "MART-NCS-BAND-MAIN", "FEEDS", "FUTURE"),
    ("MART-RQ1-GLOBAL", "RESULT-RQ1-*", "PRODUCES", "FUTURE"),
    ("RESULT-RQ1-*", "CLAIM-*", "SUPPORTS", "CONTRACT_ONLY"),
)
