# Implementation Runbook

## Phase 0 — pure bootstrap

```bash
uv sync --all-groups --locked
set -a
source env/bootstrap.env.example
set +a
uv run p4 env check
uv run p4 contract validate
uv run p4 data verify
uv run p4 status
uv run ruff check .
uv run pytest
```

Required result: `PURE_BOOTSTRAP_READY`, zero populated data files, and no
network calls.

## Phase 1 — fixture foundation

1. Add only synthetic, redistributable files under `data/fixtures/`.
2. Create parser, approval, recorder, and gate fixtures.
3. Test deterministic raw/content hashes and complete manifest fields.
4. Keep `empiricalAnalysisAllowed=false` and `promotionAllowed=false`.

Exit gate: all safety and restart tests pass without network.

## Phase 2 — observed import

1. Copy `env/observed.env.example` to an untracked operator profile.
2. Place an explicitly approved snapshot at `P4_OBSERVED_SOURCE_ROOT`.
3. Register its SHA, rows, grain, provenance, contract, and data version.
4. Run `p4 data verify` before `p4 replay observed`.
5. Write replay evidence under a new immutable run ID.

Exit gate: structural/semantic replay passes with diagnostic-only provenance.

## Phase 3 — canary implementation

1. Complete signed approval validation and budget accounting.
2. Connect index/detail/assets orchestration to `PolicyHttpClient`.
3. Complete raw-object manifest fields and checkpoint recovery.
4. Run Tier 0 fixtures first.
5. Request separate authority before any Tier 1 transport.

Exit gate: bounded canary evidence; still no empirical promotion.

## Phase 4 — production release

1. Execute the approved 2020-01 through 2026-07 collection scope.
2. Resolve raw-to-posting authority and quarantines.
3. Split tracks, parse boundaries/requirements, and perform 90-day dedup.
4. Freeze release manifest, checksums, row counts, exclusions, and coverage.

Exit gate: `PRODUCTION_RELEASE_READY` independently accepted.

## Phase 5 — NCS quality

1. Register official NCS source and hierarchy/crosswalk lineage.
2. Freeze deterministic lexical baseline.
3. Build independent reference/gold samples.
4. Evaluate precision, recall, F1, coverage, abstention, and error slices.
5. Promote only reviewed mappings.

Exit gate: `NCS_REFERENCE_READY` and mapping-quality threshold decision recorded.

## Phase 6 — marts, analysis, article results

1. Build RQ-specific marts from the accepted release.
2. Run prespecified observational analyses and robustness checks.
3. Record limitations and non-causal interpretation.
4. Generate a checksum-bound result manifest.

Exit gates: `ANALYSIS_READY`, then `ARTICLE_READY` as separate decisions.

## Evidence packet checklist

For every claimed gate record:

- status and exact gate name
- absolute artifact path
- SHA-256 and byte count
- row count and analytical grain
- command and exit code
- contract/data/release/run identifiers
- exclusions, warnings, and promotion authority
