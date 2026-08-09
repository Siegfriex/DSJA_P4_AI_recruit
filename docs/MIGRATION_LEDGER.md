# Migration Ledger

The machine-readable ledger is `manifests/legacy_sources.lock.yaml`. Every port
records repository, branch, commit, path, SHA-256, destination, action, and
reason. Generated runs and reports were not selected as source authority.

Disposition summary:

| Family | Action | Notes |
|---|---|---|
| Contract 2.1.2 | PORT | immutable compatibility snapshot |
| SourceBlock/Chunk schemas | PORT | promoted through 2.1.3 bridge |
| Collection policy/parser | PORT_AND_FIX | unified package, fail closed |
| Requirement/eligibility/labels | PORT_AND_FIX | semantic defects corrected |
| Dedup | REWRITE | observed and production modes separated |
| NCS local units/lexical | PORT | candidate only |
| Dense/reranker/LLM runtime | DROP_FOR_NOW | not executed or quality-evaluated |
| Executed notebooks | DROP | new output-free source notebooks |
| Raw/Parquet/NCS corpus | LOCAL_DATA_ONLY | SHA verified and Git ignored |
| Old reports/article drafts | ARCHIVE_REFERENCE | not copied as current authority |
