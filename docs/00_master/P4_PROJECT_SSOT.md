# P4 Project SSOT

- SSOT ID: `SSOT-P4-001`
- Version: `v1.0.0`
- Status: `FINAL_DESIGN_BASELINE`
- As-of: `2026-08-09`
- Repository: `Siegfriex/DSJA_P4_AI_recruit`
- Code baseline: `migration/bootstrap@ac2ae67fdfd3898f999a2b4cdb6a2cdcf0f31acd`

## 1. Project definition

P4는 Linkareer AI·IT 관련 채용공고에서 신입·인턴·경력 공고구조,
신입·인턴 진입장벽, 인턴 담당업무의 NCS 능력단위·공식 level/band를
재현 가능한 데이터로 구성하고 관찰적 시계열 분석을 수행한다.

## 2. Scope

```text
Source: Linkareer + NCS
Period: 2020-01 ~ 2026-07
Population: Linkareer AI·IT 관련 유효 채용공고
```

Work24/KOSIS/BOK/인터뷰/기업 공식페이지는 enrichment/context/case evidence로만 사용한다.

## 3. Non-goals

- 한국 전체 채용시장으로의 자동 일반화.
- AI의 인과효과 주장.
- 공고 수를 실제 채용인원으로 해석.
- NCS level을 개인 숙련도·직급·임금으로 해석.
- LLM_REFERENCE를 HUMAN_GOLD로 표현.
- 다른 채용플랫폼을 Linkareer denominator에 합산.

## 4. Official RQs

| ID | Official grain | Official main output |
|---|---|---|
| RQ-001 | canonical posting × month | `rq1_posting_monthly_global_mart` |
| RQ-002A | eligible track × logical fact | `rq2a_monthly_mart` |
| RQ-002B | eligible DUTY chunk × accepted NCS unit | `ncs_band_distribution_main_mart` |

## 5. Canonical fields

```text
postingEligibleFlag
rq1EligibleFlag
rq2EligibleFlag
ncsEligibleFlag
canonicalRecordFlag
```

`validPostingFlag` 금지.
`highDemandScore`는 reserved이며 NULL.

## 6. Source evidence rule

`posting_source_block`에는 HTML/ACTIVITY_TEXT/OCR 원천 span만 저장한다.
merged text는 `derived_text_view`에서 재생성한다.

## 7. Mention / Fact / Summary

```text
raw source expression
→ mention
→ normalized logical fact
→ track summary
→ mart
```

원문 mention과 분석 summary를 같은 grain으로 저장하지 않는다.

## 8. Dedup

Dedup은 물리 삭제가 아니라 duplicate group과 canonicalRecordFlag를 통한 분석 view다.
main과 pre-dedup sensitivity를 분리한다.

## 9. NCS main rule

```text
Main = SINGLE_ACCEPTED only
Sensitivity = SINGLE_ACCEPTED + MULTI_ACCEPTED, 1/k
Coverage denominator = all ncsEligible DUTY chunks
```

NCS level/band는 selected unit의 official metadata에서만 파생한다.

## 10. Publication boundary

정량 article claim은 ResultManifest가 없으면 `VERIFIED`로 승격할 수 없다.
Context/interview는 primary quantitative evidence를 대체하지 않는다.

## 11. Current implementation state

| Gate | Status |
|---|---|
| NEW_REPO_BOOTSTRAPPED | PASS |
| CONTRACT_2_1_3_READY | PASS |
| CORE_MODULES_MIGRATED | PARTIAL |
| OBSERVED_DATA_MIGRATED | PASS |
| OBSERVED_REPLAY_READY | PASS_WITH_FINDINGS |
| RAW_TO_SEMANTIC_REPLAY_READY | BLOCKED |
| CANARY_PREFLIGHT_READY | BLOCKED |
| PRODUCTION_DATA_READY | BLOCKED |
| DATA_READY_RQ1_RQ2A | BLOCKED |
| DATA_READY_RQ2B | BLOCKED |
| ANALYSIS_READY | BLOCKED |
| ARTICLE_RESULT_READY | BLOCKED |

## 12. Authority

```text
raw bytes/SHA
> immutable manifest
> contract/Git commit
> executed artifact
> tests/QA
> audit
> summary
```

최종 의사결정권자는 사용자다.
