# Detailed Design

## 1. Repository layout

| Path | Responsibility | Write policy |
|---|---|---|
| `env/` | non-secret configuration examples | tracked examples only |
| `config/` | reviewed policy, scope, periods, gates | reviewed change |
| `contracts/` | logical schema, JSON Schema, DuckDB DDL | versioned and immutable after release |
| `manifests/` | active dataset registry and checksums | generated/reviewed metadata |
| `src/p4/collection/` | approval, policy, parsing, recording | no analysis logic |
| `src/p4/processing/` | normalization, tracks, requirements, labels, dedup | no network |
| `src/p4/ncs/` | local corpus, retrieval, reference, evaluation | no promotion without quality evidence |
| `src/p4/marts/` | empirical marts and result guards | release-gated |
| `src/p4/qa/` | schema, lineage, semantic, readiness validation | read-only |
| `data/` | local machine data by lifecycle | Git ignored except placeholders |
| `artifacts/` | immutable run evidence | Git ignored except placeholders |
| `notebooks/` | thin orchestration views | source-only, output-free |

## 2. Environment contract

`Settings.from_env()` is the only path-resolution entrypoint. Relative paths
resolve from the repository root. Bootstrap defaults require no populated `.env`.

Required controls:

- `P4_RUN_MODE`: `bootstrap`, `observed`, `canary`, or `production`
- `P4_NETWORK_ENABLED`: explicit `true` or `false`
- `P4_DATA_ROOT`, `P4_ARTIFACT_ROOT`: local roots
- `P4_OBSERVED_SOURCE_ROOT`, `P4_REPLAY_OUTPUT_ROOT`: observed mode only
- `P4_NCS_UNIT_PATH`: NCS build only
- `P4_APPROVAL_FILE`: canary/production preparation only

Configuration does not load secrets or dotenv files implicitly. Invalid booleans,
unknown modes, and network-enabled bootstrap/observed configurations fail before
stage logic runs.

## 3. Data lifecycle

```text
raw (immutable bytes)
  -> staging (parsed but not promoted)
  -> processed (contract-conformant entities)
  -> reference (evaluated NCS/gold authority)
  -> releases (accepted production snapshot)
  -> marts (RQ-specific analytical grains)
  -> artifacts/reports (results and evidence)
```

No stage overwrites raw bytes or a prior run. CSV is inspection-only;
Parquet/DuckDB are machine-canonical. Every active dataset entry records ID,
path class, local path, SHA-256, rows, grain, provenance, contract version, data
version, and promotion flags.

## 4. Stage artifact contract

Each executable stage writes to `artifacts/runs/<runId>/<stageId>/`:

- `stage_manifest.json`: inputs, outputs, versions, mode, time, command, exit status
- `stage_metrics.json`: row counts and operational metrics
- `stage_quality.json`: gate checks, findings, exclusions
- `CHECKSUMS.sha256`: all stage outputs
- `stage.log`: redacted diagnostic log

`runId` and output paths are immutable. Restart creates a new attempt or resumes
through an explicit checkpoint; it never silently replaces evidence.

## 5. Collection boundary

The collection orchestrator shall:

1. load and validate a signed approval packet;
2. compare policy/query hashes and requested scope;
3. reserve a request budget before transport;
4. enforce allowed HTTPS hosts, rate, concurrency, retry, and kill switches;
5. record raw bytes and complete raw-object lineage;
6. stop on approval expiry, budget exhaustion, challenge markers, or health failure.

The current CLI validates approval binding but does not execute transport. This
is an explicit implementation gap, represented by
`COLLECTION_IMPLEMENTATION_READY=BLOCKED`.

## 6. Processing and semantic rules

- Parsing recovers source evidence before deriving labels.
- Track splitting precedes eligibility and dedup.
- Required and preferred sections remain separate.
- Atomic requirement facts are aggregated without replacing missing evidence
  with constants.
- Source authority, track resolution, boundary resolution, usable body, and
  canonical dedup are independent flags and exclusion reasons.
- Production eligibility is recomputed from current evidence; inherited booleans
  are never trusted.

## 7. NCS design

The first baseline is deterministic lexical retrieval. Candidate ranking is not
a validated mapping. Promotion requires:

- official source hash and version;
- complete hierarchy/crosswalk fields required by the selected scope;
- independent reference labels with stated authority;
- evaluated precision, recall, F1, coverage, and abstention;
- reviewed error slices and a frozen calibration version.

LLM output may be reference or model evidence but cannot imply external truth.

## 8. Analysis boundary

RQ1 uses canonical posting counts by month and track type. RQ2-A uses eligible
track/requirement grains. RQ2-B uses eligible duty chunks and quality-evaluated
NCS mappings. Monthly aggregation, HAC segmented regression, panel comparisons,
and comparable-window analysis may begin only after `ANALYSIS_READY`.

## 9. Error model

- `EMPTY_BOOTSTRAP`: expected zero-data repository state
- `BLOCKED`: prerequisite or authority absent
- `NOT_EVALUATED`: implementation/input exists but quality was not measured
- `FAIL`: an asserted contract or integrity check did not hold
- `PASS_WITH_FINDINGS`: bounded success with explicit non-promotable findings
- `PASS`: the named gate, and only that gate, passed
