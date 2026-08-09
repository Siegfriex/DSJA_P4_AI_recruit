# Data Contract 2.1.3 Bridge

Contract 2.1.3 preserves all 26 logical tables from 2.1.2 and adds three
executed semantic-lineage entities:

- `core.postingSourceBlock`
- `core.sectionSourceBlock`
- `core.semanticChunk`

Reference, calibration, API-probe, bridge, and crosswalk schemas remain
extensions until rows are executed and independently quality-evaluated.

DuckDB and Parquet are machine-canonical. CSV files are inspection exports.
Cross-schema foreign keys are logical QA rules because DuckDB does not support
the legacy cross-schema FK pattern. `validPostingFlag` is forbidden.
`highDemandScore` is reserved and must remain NULL with `scoreStatus=reserved`.
