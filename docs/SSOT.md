# P4 Single Source of Truth

## 1. Research scope

P4 studies Linkareer recruitment postings from 2020-01 through 2026-07 for a
reviewed AI·IT cohort. RQ1 measures entry/intern/experienced posting structure;
RQ2-A measures entry barriers and requirements; RQ2-B maps eligible duty
evidence to NCS units, levels, and bands.

Korea-wide labor-market, Work24, and AI-exposure causal designs are not part of
the primary scope. The 2023 breakpoint is observational and cannot identify an
“AI caused” effect.

## 2. Current authority state

The repository state is `PURE_BOOTSTRAP`.

- active dataset count: 0
- production rows: 0
- promoted NCS reference rows: 0
- mart rows: 0
- result-manifest rows: 0
- article-authoritative numbers: 0

The deleted observed-development bundle remains historical provenance only. It
is not an active input, denominator, fixture, or regression result.

## 3. Authority order

1. immutable raw bytes and content SHA-256
2. accepted release manifest and active data registry
3. current contract and schema
4. stage run manifest, metrics, quality report, and checksums
5. independently executed validators and tests
6. audit report
7. planning and historical documents

## 4. State separation

The following states must never be collapsed:

`EMPTY_BOOTSTRAP → FIXTURE → OBSERVED → CANARY → PRODUCTION_RELEASE →`
`QUALITY_EVALUATED → CANONICAL_PROMOTED → ANALYSIS_READY → ARTICLE_READY`

Each transition requires the gate defined in the design specification. Code,
an environment variable, a checksum, or a successful structural test alone is
never sufficient evidence for the next state.

## 5. Mandatory invariants

- `canonicalPostingId` is used for posting counts; `trackId` is the detail grain.
- required and preferred evidence remain distinct.
- raw, parse, source-block, chunk, label, NCS, and mart lineage is retained.
- 90-day repost dedup is required for production denominators.
- `validPostingFlag` is forbidden.
- `highDemandScore` is reserved and NULL until separately designed and approved.
- `empiricalAnalysisAllowed` and `promotionAllowed` default to false.
