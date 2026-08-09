# Defect and Gap Register

| ID | Severity | Gap | Required closure | Status |
|---|---|---|---|---|
| BOOT-P1-001 | P1 | Collection CLI validates approval but executes no transport | implement bounded orchestrator and fixture tests | OPEN |
| BOOT-P1-002 | P1 | Approval has no signer/signature or budget-consumption verification | define signed schema and atomic budget ledger | OPEN |
| BOOT-P1-003 | P1 | No production source data or accepted 79-month release | separately approve, collect, QA, and freeze release | OPEN |
| BOOT-P1-004 | P1 | NCS reference hierarchy/bridge/gold quality absent | register official source and evaluate mapping | OPEN |
| BOOT-P1-005 | P1 | RQ marts, analysis, and result manifest absent | build only after upstream gates | OPEN |
| BOOT-P2-001 | P2 | Recorder metadata is not yet the complete raw-object manifest contract | add content hash, compressed bytes, source fingerprint, IDs | OPEN |
| BOOT-P2-002 | P2 | Critical approval, parser, QA, CLI, and restart paths need broader tests | add fixture-based coverage and failure cases | OPEN |

Legacy defects and their prior replay observations are historical context in
`MIGRATION_AUDIT.md`; they are not active-data findings in the pure repository.
