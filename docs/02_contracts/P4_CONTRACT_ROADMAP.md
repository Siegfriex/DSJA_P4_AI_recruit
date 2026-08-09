# P4 Contract Roadmap

| Version | Scope | Promotion gate |
|---|---|---|
| 2.1.3 | Legacy compatibility + SourceBlock/SectionSourceBlock/SemanticChunk | current bridge validated |
| 2.2.0 | Evidence lineage: ChunkSourceBlock, DerivedText, Company identity, Taxonomy release | raw→semantic E2E + bridge coverage |
| 2.3.0 | Mention/Fact/Extension semantic system | sampled semantic validation + frozen taxonomies |
| 2.4.0 | NCS candidate/source-score/reference normalization | provenance + terminal completeness + multi-label rule |
| 3.0.0 | Production marts / ResultManifest / Article Claim | denominator audit + publication integrity |

## 2.2 gates
- section evidence coverage = 100% for eligible section.
- chunk primary evidence coverage = 100% for eligible chunk.
- orphan FK = 0.
- derived merge deterministic replay = 100%.
- sourceMode outside HTML/ACTIVITY_TEXT/OCR = 0.

## 2.3 gates
- mention→fact evidence lineage = 100%.
- taxonomy frozen.
- unknown/conflict rates reportable.
- validation artifact exists.

## 2.4 gates
- candidate provenance complete.
- candidate and candidate-source uniqueness complete.
- terminal mapping state completeness = 100%.
- main/sensitivity aggregation contract frozen.

## 3.0 gates
- RQ denominator audit PASS.
- sourceMode/job/month coverage report exists.
- audit-period taxonomy leakage = 0.
- ResultManifest / article claim evidence integrity complete.
