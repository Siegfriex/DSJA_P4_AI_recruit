# P4 데이터 제품/분석 설계서
## Data Product Design Document & Project SSOT Master Blueprint

### 0. 문서 통제 표지

| 항목 | 값 |
|---|---|
| 문서 ID | `DPDD-P4-001` |
| 프로젝트 ID | `P4-AI-RECRUIT` |
| 문서명 | P4 데이터 제품/분석 설계서 |
| 버전 | `v1.0.0` |
| 기준일 | `2026-08-09` |
| 문서 상태 | `FINAL_DESIGN_BASELINE` |
| 적용 범위 | Linkareer + NCS, 2020-01~2026-07, AI·IT 채용공고 관찰연구 |
| 코드 저장소 | `Siegfriex/DSJA_P4_AI_recruit` |
| 로컬 기준경로 | `/home/sieg/projects-wsl/DSJA_P4_AI_recruit` |
| 구현 기준 branch | `migration/bootstrap` |
| 구현 기준 SHA | `ac2ae67fdfd3898f999a2b4cdb6a2cdcf0f31acd` |
| main SHA | `e94913c8c105120b3b811b444dc759ddf3628c5f` |
| 최종 의사결정권자 | 사용자 |
| Production 승인 | 별도 승인 필요 |
| 기밀 등급 | 문서 공개 가능 / raw 및 local empirical data는 별도 통제 |
| 변경 등급 | Semantic Versioning: Major / Minor / Patch |

### Executive verdict

본 문서는 P4를 단순한 크롤링·모델 프로젝트가 아니라 다음의 연쇄로 정의한다.

```text
immutable source evidence
→ normalized recruitment entities
→ atomic semantic mentions/facts
→ denominator-safe analytical marts
→ NCS reference mapping
→ statistical results
→ ResultManifest
→ article claims
```

현재 문서 아키텍처와 target architecture는 최종 기준선으로 고정할 수 있다.
그러나 현재 새 코드베이스의 collection producer와 raw→semantic producer chain은 아직 완결되지 않았다.
따라서 문서 승격과 production 승격을 분리한다.

```text
DOCUMENTATION_BASELINE_READY   = PASS
CONTRACT_2_1_3_READY           = PASS
CORE_MODULES_MIGRATED          = PARTIAL
RAW_TO_SEMANTIC_REPLAY_READY   = BLOCKED
CANARY_PREFLIGHT_READY         = BLOCKED
PRODUCTION_DATA_READY          = BLOCKED
DATA_READY_RQ1_RQ2A            = BLOCKED
DATA_READY_RQ2B                = BLOCKED
ANALYSIS_READY                 = BLOCKED
ARTICLE_RESULT_READY           = BLOCKED
```

---

# 1. 문서 개요 및 거버넌스

## 1.1 문서 목적

P4 SSOT는 다음 질문에 항상 하나의 authoritative answer를 제공해야 한다.

- 연구가 무엇을 측정하는가?
- 어떤 공고가 분석 모집단에 포함되는가?
- 각 테이블·필드·지표의 공식 정의는 무엇인가?
- 원문의 어떤 span이 어떤 fact·label을 지지하는가?
- NCS code·level·band는 어떤 corpus release와 mapping authority에서 왔는가?
- 어떤 result가 어떤 run·manifest·QA를 거쳐 기사 숫자가 되었는가?

Normative specification과 empirical evidence는 분리한다.

| 구분 | 의미 |
|---|---|
| Normative specification | 앞으로 무엇을 어떻게 계산할지 고정 |
| Empirical evidence | 실제 실행에서 무엇이 관찰됐는지 기록 |

설계 문서가 실행 증적을 덮어쓰거나, 실행 보고서가 연구정의를 임의 변경해서는 안 된다.

## 1.2 권위 위계

```text
1. immutable raw bytes / SHA-256
2. immutable release or evidence manifest
3. Git commit / versioned contract
4. executed stage artifact
5. tests / validators / QA
6. audit report
7. descriptive summary
```

## 1.3 RACI

| 역할 | 책임 |
|---|---|
| User / Final Approver | 연구범위, network crawl, publication, major contract 변경 최종 승인 |
| Cloud Meta-Orchestrator | 다중 Agent 증거 대조, gate 판정, SSOT 통합, 사용자 의사결정 지원 |
| Local Codebase Orchestrator | 실제 코드·로컬 데이터·테스트·SHA 기반 구현 및 감사 |
| Collection Owner | Linkareer 수집, raw lineage, source policy |
| Semantic/Data Owner | normalize, track, section, fact, eligibility, dedup |
| NCS Owner | NCS corpus, retrieval, reference, evaluation |
| Analysis Owner | RQ mart, 통계분석, result manifest |
| Article Owner | claim-evidence 연결, 기사 숫자 parity |

## 1.4 변경관리

- Patch: 계산에 영향 없는 문구·메타데이터.
- Minor: backward-compatible schema/sidecar/feature 추가.
- Major: 모집단, 기간, denominator, dedup, taxonomy semantics, metric 공식, NCS main aggregation 규칙 변경.

Major 변경은 영향 분석 → 재실행 → 재평가 → 재승인 → 새 Release Manifest를 요구한다.

---

# 2. 사업 배경과 문제정의

P4는 AI·IT 채용공고에서 신입·인턴·경력 모집구조와 진입장벽, 인턴 담당업무의 구조를
시계열로 관찰하기 위한 데이터 저널리즘·연구 데이터 제품이다.

핵심 문제는 자연어·이미지 중심의 채용공고가 바로 분석 가능한 정형 데이터가 아니라는 점이다.
공고 수만 세면 모집유형·재게시·복수 직무·명시되지 않은 요구조건·이미지 본문·업무/우대 조건이
혼합되어 denominator와 의미가 깨진다.

P4가 해결하려는 것은 다음이다.

- 모집공고를 재현 가능한 canonical entity로 변환한다.
- 요구조건과 담당업무를 evidence span에 연결된 atomic fact로 만든다.
- RQ별 분석 grain과 denominator를 분리한다.
- 인턴 업무를 NCS 능력단위 및 공식 level/band와 연결하되 불확실성을 보존한다.
- 최종 기사 claim을 ResultManifest와 source evidence까지 역추적한다.

해결하지 않는 문제:

- 한국 전체 노동시장에 대한 전수 추정.
- AI가 채용구조 변화를 야기했다는 인과 추론.
- NCS level을 개인 숙련도·임금·직급으로 해석.
- 공고 수를 실제 채용 인원으로 해석.
- LLM_REFERENCE를 HUMAN_GOLD로 간주.

---

# 3. 목표·범위·성공 기준

## 3.1 연구질문

| ID | 질문 | 공식 grain | Primary output |
|---|---|---|---|
| `RQ-001` | 신입·인턴·경력 공고구조는 시점별로 어떻게 관찰되는가 | canonical posting × month | RQ1 global posting mart |
| `RQ-002A` | 신입·인턴 진입장벽과 요구조건은 어떻게 변하는가 | track × logical requirement | RQ2-A track/month mart |
| `RQ-002B` | 인턴 담당업무는 어떤 NCS 능력단위·공식 수준에 대응하는가 | DUTY chunk × accepted NCS unit | RQ2-B NCS marts |
| `MQ-001` | source recovery와 semantic lineage 품질은 어느 정도인가 | source block / chunk | source recovery QA |
| `MQ-002` | NCS candidate/mapping coverage와 불확실성은 어느 정도인가 | eligible DUTY chunk | mapping coverage mart |

## 3.2 모집단과 기간

```text
Primary population:
Linkareer에서 확인되는 AI·IT 관련 유효 채용공고

Primary time window:
2020-01 ~ 2026-07 (79 months)

Primary denominator authority:
Linkareer only
```

NCS는 RQ2-B reference source이며 Linkareer denominator에 행을 추가하지 않는다.
Work24·KOSIS·한국은행·인터뷰는 enrichment/contextual sidecar다.

## 3.3 성공 기준 계층

기술적 성공과 연구 성공을 분리한다.

1. Source success: 수집 coverage, raw SHA, terminal state.
2. Semantic success: posting/track/section/chunk/fact evidence completeness.
3. Reference success: candidate provenance, mapping terminal state, quality evaluation.
4. Analytical success: denominator audit, sensitivity, time coverage.
5. Publication success: ResultManifest + claim evidence linkage.

---

# 4. 데이터 전략 및 수집 설계

## 4.1 Source classification

| Source | 역할 | Population denominator |
|---|---|---|
| Linkareer index/detail | `PRIMARY_CANONICAL` | 포함 |
| Linkareer hosted asset/OCR | `PRIMARY_CANONICAL` 보조 원문 | 포함되는 posting의 evidence만 보강 |
| NCS | `NCS_CANONICAL` | 미포함 |
| Work24 alias/crosswalk | `ENRICHMENT` | 미포함 |
| KOSIS/BOK/고용24 통계 | `CONTEXTUAL` | 미포함 |
| Interview/case validation | `QUALITATIVE/CASE` | 미포함 |

## 4.2 Linkareer 목표 collection

```text
S0 Month Plan
→ S1 APQ Index Discovery
→ S2 Detail Fetch / Raw Posting Version
→ S3 Linkareer-hosted Asset / OCR
→ immutable manifests
```

Target source policy:

- HTTPS Linkareer host only.
- External ATS transport prohibited.
- approval-file binding required for network runs.
- rate limit ≤ 1 request/sec.
- concurrency ceiling ≤ 2 and must be actually enforced.
- retry/backoff and 403/429/challenge kill switches.
- month/request budget bound to approval artifact.
- all accepted raw bytes content-addressed with SHA.

## 4.3 Current implementation reality

현재 새 repository에는 source policy·approval guard·detail parser 일부가 존재하지만,
APQ pagination/frontier/checkpoint/detail fetch/asset fetch와 실제 CLI transport binding은 미완이다.

따라서 `networkCalls=0` 유지 상태에서 collector hardening이 선행되어야 한다.

---

# 5. 데이터 명세 및 Data Card

## 5.1 Layer model

```text
SOURCE_EVIDENCE
CANONICAL_ENTITY
ATOMIC_MENTION
LOGICAL_FACT
DERIVED_SUMMARY
REFERENCE_RETRIEVAL
REFERENCE_MAPPING
ANALYTICAL_MART
PUBLICATION_EVIDENCE
```

## 5.2 핵심 entity

| Entity | Grain | PK | 의미 |
|---|---|---|---|
| `raw_posting_version` | posting × retrieval version | `rawPostingId` | immutable source |
| `posting_source_block` | raw source span | `sourceBlockId` | HTML/ActivityText/OCR evidence |
| `posting_normalized` | posting | `postingId` | canonical posting |
| `posting_track` | recruitment track | `trackId` | 복수 모집 트랙 |
| `posting_section` | track semantic section | `sectionId` | DUTY/REQUIRED/PREFERRED 등 |
| `section_source_block` | section×block | composite | N:M source lineage |
| `semantic_chunk` | atomic semantic span | `chunkId` | 모델/fact 최소 입력 |
| `chunk_source_block` | chunk×block | composite | N:M evidence lineage |
| `requirement_mention` | raw expression | `mentionId` | 관측 표현 |
| `requirement_fact` | normalized logical requirement | `requirementFactId` | 논리 사실 |
| `skill_requirement_fact` | normalized skill condition | `skillFactId` | 기술·행위·의무성 |
| `selection_process_stage_fact` | explicit selection stage | `selectionStageId` | 공고상 명시 단계 |
| `duty_action_mention` | duty action mention | `dutyActionMentionId` | 업무유형과 책임수준 |
| `ncs_candidate` | run×chunk×NCS unit | `candidateId` | union candidate |
| `ncs_candidate_source_score` | candidate×retrieval source | composite | retrieval contribution |
| `ncs_mapping_reference` | accepted/rejected mapping | `mappingId` | reference authority |
| RQ marts | RQ-specific | contract-specific | 최종 분석 |

## 5.3 SourceBlock 불변 규칙

`posting_source_block.sourceMode`는 다음만 허용한다.

```text
HTML
ACTIVITY_TEXT
OCR
```

`MERGED`는 금지한다. 병합 텍스트는 `derived_text_view`에서만 생성하며 원천 block을 대체하지 않는다.

## 5.4 Canonical fields

```text
postingEligibleFlag
rq1EligibleFlag
rq2EligibleFlag
ncsEligibleFlag
```

`validPostingFlag`는 canonical field로 사용하지 않는다.

`highDemandScore`는 reserved이며 전 행 NULL 상태를 유지한다.

---

# 6. 데이터 품질 진단

행수 대소관계를 품질계약으로 사용하지 않는다. 문서 구조상 정상적으로 깨질 수 있기 때문이다.

대신 아래 integrity/coverage contract를 사용한다.

```text
orphan PK/FK = 0
eligible section with no source evidence = 0
eligible chunk with no PRIMARY evidence = 0
eligible DUTY chunk with no terminal mapping state = 0
canonical posting with no dedup membership = 0
duplicate(candidateRunId, chunkId, ncsUnitCode) = 0
```

핵심 coverage:

- detailTerminalCoverage
- rawFetchCoverage
- normalizationCoverage
- sectionEvidenceCoverage
- chunkPrimaryEvidenceCoverage
- pathwayResolutionRate
- selectionDisclosureRate
- mappingSingleCoverage
- mappingAnyAcceptedCoverage
- OCR parse/mapping eligibility coverage

현재 observed migration inventory는 regression evidence로만 보존한다.

```text
posting               137
raw HTML                29
source block             84
semantic chunk          277
requirement fact         41
NCS local unit       13,442
NCS legacy candidate    128
structural reference     27
```

이 숫자는 production 모집단 결과가 아니다.

---

# 7. 파이프라인·통합 설계

## 7.1 최종 Stage Order

```text
S0  period config → month plan
S1  index discovery
S2  detail raw / raw posting version
S3  asset fetch / OCR (optional branch)
S4  posting normalization
S5  posting SourceBlock extraction
S6  track split
S7  section segmentation + section_source_block
S8  semantic chunking + chunk_source_block
S9  atomic mention/fact extraction
S10 career/intern/pathway/selection/skill/duty classification
S11 dedup group formation + canonical record selection
S12 RQ1 / RQ2-A marts
S13 NCS corpus freeze
S14 candidate generation
S15 source score / fusion / rerank / reference
S16 accepted mapping terminalization
S17 official NCS level/band derivation
S18 RQ2-B marts
S19 statistical analysis
S20 contextual / qualitative sidecars
S21 ResultManifest / article claim registry
```

SourceBlock은 원문 evidence이므로 Section보다 먼저 생성한다.

## 7.2 Join principles

- SourceBlock↔Section = N:M bridge.
- Chunk↔SourceBlock = N:M bridge.
- Requirement mention↔Logical fact = N:M 허용.
- Candidate↔retrieval source score = 1:N.
- Work24는 candidate generation enrichment이며 NCS canonical unit을 대체하지 않는다.
- Contextual/qualitative source는 primary analysis mart denominator에 join하지 않는다.

## 7.3 Dedup

Dedup은 delete가 아니라 analysis-time canonicalization이다.
모든 raw/normalized/fact row는 보존하고 `canonicalRecordFlag`로 main denominator를 선택한다.
pre-dedup 결과는 sensitivity로 별도 산출한다.

---

# 8. 전처리·정규화 설계

전처리는 방법이 아니라 의사결정으로 기록한다.

모든 변환은 최소 다음을 기록한다.

- input/output dataset ID와 SHA.
- 대상 필드 및 grain.
- 결측·unknown·conflict 처리.
- 처리 전후 row/coverage 분포.
- producer code commit/module SHA/version.
- taxonomy version.
- 실행일/run ID.
- 잔여 위험.

핵심 정규화:

1. source identity / URL / raw SHA.
2. canonicalPostedAt / periodMonth.
3. company legal entity 및 alias.
4. track split.
5. section boundary.
6. source evidence block.
7. semantic chunk.
8. mention → logical fact.
9. requirement obligation 및 conflict.
10. skill taxonomy.
11. duty workStage와 responsibilityLevel.
12. 90-day repost group.

`requirement_mention → requirement_fact → track_requirement_summary` 세 grain을 분리한다.
동일 조건이 REQUIRED와 PREFERRED에 모두 있으면 원 fact를 삭제하지 않고 summary에서만 conflict/resolution을 계산한다.

---

# 9. 분석·모델링 설계

## 9.1 문제 유형

P4의 주 분석은 예측이 아니라:

```text
기술통계
기간별·집단별 차이
패턴
상관 및 조건부 연관성
sensitivity analysis
```

이다.

## 9.2 Target과 Feature 분리

RQ1 target:
- entry/intern/experienced/mixed posting structure.

RQ2-A target:
- careerClass, internAccessClass, pathway, requirements 및 track-level barrier metrics.

RQ2-B target:
- DUTY chunk의 accepted NCS unit, official level, NCS band.

Raw/semantic features:
- source mode, section type, requirement type, normalized skill, obligation, action level,
  work stage, responsibility level.

## 9.3 Baseline과 후보 모델

### Semantic extraction
- deterministic rules / dictionaries first.
- LLM은 ambiguous semantic classification/reference에 제한적으로 사용.
- `LLM_REFERENCE != HUMAN_GOLD`.

### NCS retrieval
Current baseline:
- token overlap lexical baseline.

Target candidates:
- BM25.
- dense multilingual/Korean embedding.
- exact/curated alias.
- optional Work24 alias.
- candidate union.
- cross-encoder or LLM reranker.
- LLM_REFERENCE / adjudication.
- calibration and abstention.

### Statistical analysis
- monthly descriptive aggregation.
- 2023 observational breakpoint.
- segmented regression + Newey-West HAC.
- job×month panel / job FE where justified.
- 2026 comparable-window/YTD analysis.
- breakpoint sensitivity.

2023 breakpoint는 관찰적 비교 기준이며 인과 개입시점으로 해석하지 않는다.

## 9.4 Temporal leakage control

권고 split:

```text
Development: 2020–2024
Validation:  2025
Frozen audit: 2026 YTD
```

job/skill/work-stage/pathway taxonomy는 frozen audit를 보기 전에 고정한다.
2026에서 새 개념이 발견되면 `UNKNOWN` 또는 `DRIFT_CANDIDATE`로 보낸다.

---

# 10. 평가·검증·수용 설계

## 10.1 세 층 평가

1. 데이터/기술: integrity, coverage, extraction precision/recall, retrieval Recall@K, mapping precision/coverage.
2. 연구/업무: denominator 안정성, unknown/abstain, sensitivity, 재현성.
3. publication: ResultManifest parity, evidence traceability, causal-overclaim prevention.

## 10.2 RQ2-B multi-label rule — Frozen

Main:

```text
NCS band main distribution = SINGLE_ACCEPTED only
```

Sensitivity:

```text
SINGLE_ACCEPTED + MULTI_ACCEPTED
MULTI_ACCEPTED unit weight = 1 / accepted unit count
```

모든 `ncsEligible DUTY`를 coverage 분모로 별도 공개한다.

Main과 sensitivity 방향이 다르면 robust main conclusion으로 승격하지 않는다.

## 10.3 Evaluation authority

`HUMAN_GOLD`, `LLM_REFERENCE`, `SILVER`, `MODEL_PREDICTION`을 분리한다.
LLM_REFERENCE 자체의 내부 합의도를 외부 정확도로 표현하지 않는다.

---

# 11. 보안·법·윤리·리스크

핵심 통제:

- raw HTML/assets/Parquet/DuckDB는 Git 비추적.
- public repository에는 schema/code/manifest/SHA/small fixtures만 포함.
- `.env`, API key, secret은 commit 금지.
- external ATS transport 금지.
- source-policy 및 승인 artifact 없는 network collection 금지.
- interview는 consent 및 quote verification 상태 기록.
- 기사 causal overclaim 금지.
- 공고에서 관찰되지 않은 정보를 0 또는 부재로 단정하지 않는다.
- `NOT_STATED`, `UNKNOWN`, `ABSTAIN`을 명시적 상태로 보존한다.

주요 리스크:

- historical source coverage bias.
- OCR time/job/company bias.
- taxonomy temporal leakage.
- company over-merge.
- detailed-JD overcount.
- NCS candidate/reference uncertainty.
- multi-label aggregation sensitivity.
- stale document / artifact authority drift.

---

# 12. 구현·운영·유지보수

## 12.1 Canonical environment

```text
Python 3.12
uv.lock
src/p4 single package
DuckDB/Parquet machine canonical
CSV inspection/export
source notebooks output-free
```

## 12.2 Run reproducibility

모든 production-capable run은 다음 attestation을 남긴다.

```text
runId
codeCommit
contractVersion
taxonomyVersions
inputManifestSha256
rawManifestSha256
outputManifestSha256
rowCounts
schemaSignatures
testLogSha256
networkCalls
qualityResults
```

## 12.3 Monitoring

- monthly coverage / terminal state.
- source policy blocks.
- raw/parser failure.
- section/chunk evidence coverage.
- unknown/conflict rate.
- taxonomy drift queue.
- NCS candidate/mapping terminal distribution.
- mart denominator equality.
- result manifest parity.

---

# 13. 최종 결과·의사결정·로드맵

## 13.1 세 단계 제품 시나리오

### Scenario A — Core Production
Linkareer HTML/ActivityText → canonical data → Requirement/Labels/Dedup → RQ1/RQ2-A.

### Scenario B — Semantic/NCS Enriched
A + Asset/OCR + pathway/selection/skill/duty facts + hybrid NCS retrieval/reference → RQ2-B.

### Scenario C — Publication Evidence Mesh
B + BOK/KOSIS/고용24 contextual series + official case validation + interview coding
→ ResultManifest + Article Claim Registry.

## 13.2 Contract evolution

```text
2.1.3  legacy compatibility bridge
2.2.0  evidence lineage completion
2.3.0  semantic mention/fact system
2.4.0  NCS retrieval/reference normalization
3.0.0  production mart/publication SSOT
```

각 버전은 gate를 통과해야 다음 버전으로 승격한다.

## 13.3 Immediate roadmap

```text
1. bootstrap PR hardening
2. APQ/index/detail/raw collector producer 복구
3. SourceBlock/normalize/track/section/chunk/fact producer 복구
4. raw29 local E2E replay
5. Contract 2.2.0 freeze
6. Canary T1→T4
7. 79-month production crawl/release
8. RQ1/RQ2-A production marts
9. Contract 2.3.0 semantic extensions
10. Contract 2.4.0 NCS retrieval/reference
11. RQ2-B
12. Contract 3.0.0 analysis/publication
13. ResultManifest
14. article evidence linkage
```

현재 다음 단계의 가장 중요한 gate는 `RAW_TO_SEMANTIC_REPLAY_READY`이다.
문서화 완료를 production 완료로 승격하지 않는다.
