<!-- GENERATED_FILE -->
<!-- generatorVersion: p4-docs-1.0.0 -->
<!-- generatedAt: 2026-08-09T15:38:01+09:00 -->
<!-- codeCommit: ec678fc5dedc0234e7b36edca891d8183f018736 -->
<!-- inputArtifactSha: 0fefd5fea824d6bc89d629c9ddc473740dc9814e0178e68aa6d99aa83c9e3a01 -->
# P4 Current State

## Git

- Branch: `refactor/ssot-v1.0.0-cleanroom`
- Snapshot HEAD (latest code/config commit): `ec678fc5dedc0234e7b36edca891d8183f018736`
- main HEAD: `e94913c8c105120b3b811b444dc759ddf3628c5f`
- Dirty implementation inputs: `false`

## Code and tests

- Package version: `1.0.0`
- Contract version: `2.1.3`
- Implemented modules: `37`
- Tests: `22 passed / 0 failed / 0 skipped`

## Data and network authority

- Tracked synthetic fixture rows: `3`
- Local empirical registry count: `0`
- Production rows: `0`
- Linkareer live calls: `0`
- External ATS calls: `0`
- Credentialed API calls: `0`
- Data authority: `FIXTURE_EXECUTED` and local `OBSERVED_EXECUTED_NOT_PROMOTED`; canary/production/analysis remain blocked

## Gates

| Gate | Status |
|---|---|
| CLEANROOM_REPO_READY | PASS |
| DPDD_SSOT_V1_IMPORTED | PASS_WITH_FINDINGS |
| LEGACY_CLEANUP_READY | PASS |
| DOC_AUTOMATION_READY | PASS |
| COLLECTION_PRODUCER_READY | PASS |
| RAW_TO_SEMANTIC_REPLAY_READY | PASS_WITH_FINDINGS |
| STRUCTURAL_QA_READY | PASS |
| SEMANTIC_QA_READY | NOT_EVALUATED |
| CANARY_PREFLIGHT_READY | PARTIAL |
| MAIN_PROMOTION_READY | PASS_WITH_FINDINGS |
| CRAWL_RELEASE_READY | BLOCKED |
| DATA_READY_RQ1_RQ2A | BLOCKED |
| DATA_READY_RQ2B | BLOCKED |
| ANALYSIS_READY | BLOCKED |
| ARTICLE_RESULT_READY | BLOCKED |
