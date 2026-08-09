# System Design Specification

## 1. Purpose and acceptance target

The system shall turn explicitly authorized Linkareer source material and an
officially traceable NCS reference into reproducible research marts without
allowing fixture, observed, or unevaluated data to become empirical authority.

The repository is implementation-ready when a developer can configure a mode,
validate the contract, register an input, run one bounded stage, and obtain a
manifested artifact without changing code or inventing paths.

## 2. System context

```text
operator approval
       |
       v
Linkareer -> raw recorder -> parser -> posting/track/section -> semantic chunks
                                                         |             |
official NCS source -> reference validation -> retrieval/evaluation --------+
                                                                       |
                                                                       v
release manifest -> eligibility/dedup -> RQ marts -> analysis -> result manifest
```

All arrows are file- or contract-bound handoffs. Network transport is confined
to the collection boundary. Analysis cannot call a provider or mutate raw data.

## 3. Functional requirements

| ID | Requirement | Acceptance evidence |
|---|---|---|
| FR-001 | Load explicit environment profiles without committing secrets | `p4 env check` |
| FR-002 | Validate the selected contract and DuckDB DDL | `p4 contract validate` |
| FR-003 | Treat zero registered datasets as a valid bootstrap state | `p4 data verify` returns `EMPTY_BOOTSTRAP` |
| FR-004 | Reject network use outside canary/production | configuration and policy tests |
| FR-005 | Bind collection to approval, policy hash, registry hash, scope, expiry, and budget | approval validator and tests |
| FR-006 | Record raw compressed and content hashes plus redacted request lineage | raw manifest validator |
| FR-007 | Preserve posting → track → section → requirement/chunk lineage | PK/FK QA report |
| FR-008 | Fail closed when source, track, boundary, body, or dedup authority is unresolved | eligibility tests and quality report |
| FR-009 | Evaluate NCS reference and mapping quality before promotion | gold/reference evaluation artifact |
| FR-010 | Build RQ marts only from an accepted production release | mart provenance guard |
| FR-011 | Create article results only after analysis-ready gates pass | signed result manifest |

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-001 | Local-first: machine data is outside Git and addressed by SHA-256. |
| NFR-002 | Deterministic: seeds, versions, inputs, outputs, and row counts are manifested. |
| NFR-003 | Restartable: each stage has an immutable run ID and does not overwrite prior runs. |
| NFR-004 | Fail closed: missing authority produces `BLOCKED`, never an optimistic default. |
| NFR-005 | Observable: every stage emits manifest, metrics, quality, checksums, and logs. |
| NFR-006 | Safe collection: HTTPS allowlist, one request/second, concurrency two, bounded retry, kill switches. |
| NFR-007 | Non-causal reporting: association and causation language remain distinct. |

## 5. Run modes

| Mode | Network | Data authority | Permitted purpose |
|---|---|---|---|
| bootstrap | no | none | contract, code, tests, design |
| fixture | no | fixture only | deterministic unit/integration checks |
| observed | no | diagnostic only | local replay and defect regression |
| canary | approval-bound | non-empirical | bounded transport validation |
| production | approval/release-bound | potential empirical input | complete collection and release |

## 6. Promotion gates

1. `REPOSITORY_BOOTSTRAP_READY`
2. `DESIGN_SPEC_READY`
3. `CONTRACT_BRIDGE_READY`
4. `ENVIRONMENT_TEMPLATE_READY`
5. `SOURCE_DATA_READY`
6. `COLLECTION_IMPLEMENTATION_READY`
7. `PRODUCTION_RELEASE_READY`
8. `SEMANTIC_QUALITY_READY`
9. `NCS_REFERENCE_READY`
10. `ANALYSIS_READY`
11. `ARTICLE_READY`

Every PASS must point to a file, SHA-256, row count, command, exit code, and run
artifact. “Implemented” and “executed successfully” are separate claims.

## 7. Excluded from the initial implementation

- unrestricted or unapproved crawling
- external ATS collection
- provider-dependent analysis
- dense retrieval, reranking, or LLM labeling without an evaluated baseline
- causal claims about AI adoption
- automatic PR merge, production promotion, or article publication
