# Data Contract 2.1.3 Bridge

Contract 2.1.3 preserves all 26 logical tables from 2.1.2 and adds three
semantic-lineage entities: `core.postingSourceBlock`,
`core.sectionSourceBlock`, and `core.semanticChunk`.

The contract is ready; the active dataset registry is intentionally empty.
Schema readiness must not be reported as data readiness.

Future registered datasets must include dataset ID, path class, local path,
SHA-256, bytes, rows, grain, source and retrieval lineage, contract/data/release
versions, provenance, and promotion flags. DuckDB and Parquet are canonical;
CSV is inspection-only. Cross-schema foreign keys are logical QA rules.

`validPostingFlag` is forbidden. `highDemandScore` is reserved and must remain
NULL with `scoreStatus=reserved` until a separate approved design exists.
