# P4 Clean Consolidation Migration Audit

## 1. Executive verdict

The clean repository is a usable canonical development candidate with findings.
Contract 2.1.3, selected core modules, local data verification, and observed
replay are complete. Production collection, NCS quality promotion, RQ marts,
analysis, and article results remain blocked.

## 2. Legacy authority selected

- M1.5 source/data: `integration/p4-m1_5-unified-reconciliation-v2` at
  `f30f1a386895ac4f165ed390ee038a833c2a8012`
- independent audit: `audit/p4-m1_5-a5-unified-v1` at
  `06cd0cb4cb3726b1408dce58ad24f935ca008de9`
- canary controls: `integration/p4-canary-acceptance-v1` at
  `8a15618fd0d45d15c6fd2e9c04de55fb21700428`
- research design: `docs/p4-final-design-v4` at
  `9a5e49d7ba73c81c3dc65b080bf267bc22f30936`

Exact path and file SHA authority is frozen in
`manifests/legacy_sources.lock.yaml`.

## 3. New repository state

- repository: `Siegfriex/DSJA_P4_AI_recruit`
- branch: `migration/bootstrap`
- base main: `e94913c`
- remote: `https://github.com/Siegfriex/DSJA_P4_AI_recruit.git`

## 4. Migrated modules

- unified `p4.collection`, including approval binding, host restriction,
  retry/backoff, 403/429/success-rate kill switches, SSR recovery, recorder,
  asset filtering, and canary budgets
- `p4.processing` requirement aggregation, fail-closed eligibility, career
  labels, explicit track-split status, 90-day dedup, and local observed replay
- local NCS corpus validation, deterministic lexical baseline, explicit
  reference authority, calibration/evaluation boundaries
- empirical mart and result-manifest guards
- contract, raw SHA, CSV/Parquet/DuckDB, structural, semantic, and gate QA

Dense retrieval, reranking, LLM runtime, historical executed notebooks, old
runs, old reports, and article drafts were intentionally not ported as current
authority.

## 5. Contract 2.1.3

All 26 logical tables from 2.1.2 are retained. Three executed entities are
added: `core.postingSourceBlock`, `core.sectionSourceBlock`, and
`core.semanticChunk`. Contract and DuckDB DDL validation report 29/29 physical
tables. `validPostingFlag` is forbidden and `highDemandScore` remains NULL.

## 6. Local data inventory

| Dataset | Rows | SHA-256 / status |
|---|---:|---|
| raw gzip objects | 29 | 29/29 compressed/content SHA and bytes PASS |
| observed posting | 137 | `915f147e6d81...` |
| source block | 84 | `30f5e1c9032d...` |
| semantic chunk | 277 | `8a9a3c98077a...` |
| requirement fact | 41 | `ee1564520f19...` |
| NCS unit candidate | 13,442 | `b5b02ea23229...` |

All files are Git ignored; only manifests and checksums are tracked.

## 7. Observed replay comparison

| Entity | Old | New | Delta | Classification |
|---|---:|---:|---:|---|
| posting | 137 | 137 | 0 | EXPECTED |
| track | 137 | 137 | 0 | EXPECTED |
| section | 84 | 84 | 0 | EXPECTED |
| source block | 84 | 84 | 0 | EXPECTED |
| semantic chunk | 277 | 277 | 0 | EXPECTED |
| requirement fact | 41 | 41 | 0 | EXPECTED |
| NCS candidate | 128 | 128 | 0 | EXPECTED |

Intentional semantic changes:

- degree features restored for 10 tracks
- certificate features restored for 2 tracks
- posting eligibility 137 → 29
- RQ1 eligibility 137 → 11
- RQ2 eligibility 113 → 10
- NCS eligibility 55 → 10
- resolved required/preferred label boundary 0 → 28

These reductions are fail-closed corrections, not data loss.

## 8. QA and tests

- contract: 26 legacy + 3 executed semantic entities, PASS
- PK checks: 0 violations across eight primary grains
- FK checks: 0 violations across ten relationships
- CSV ↔ Parquet row equality: 12/12
- DuckDB ↔ Parquet row equality: 12/12
- invalid posting kind: 0
- non-null high-demand score: 0
- local tests: 13 passed
- source notebooks: 9/9 output-free
- Linkareer/external ATS/browser/credentialed API calls: 0

## 9. Remaining defects

- 108/137 source-authority unresolved postings remain diagnostic-only.
- Observed tracks preserve an explicit legacy single-track status; a production
  multi-track split is not claimed.
- NCS remains 27 `REVIEW_REQUIRED` + 1 `UNMAPPED`; quality is not evaluated.
- Tier 1 approval is absent and collection remains blocked.
- No production rows, marts, analysis, result manifest, or article numbers exist.

## 10. Migration gates

| Gate | Status |
|---|---|
| NEW_REPO_BOOTSTRAPPED | PASS |
| LEGACY_PROVENANCE_FROZEN | PASS |
| CONTRACT_2_1_3_READY | PASS |
| CORE_MODULES_MIGRATED | PASS_WITH_FINDINGS |
| OBSERVED_DATA_MIGRATED | PASS |
| OBSERVED_REPLAY_READY | PASS_WITH_FINDINGS |
| STRUCTURAL_QA_READY | PASS |
| SEMANTIC_REMEDIATION_READY | PASS_WITH_FINDINGS |
| CANARY_PREFLIGHT_READY | PARTIAL |

The new repository is suitable as a canonical development base:
`PASS_WITH_FINDINGS`.
