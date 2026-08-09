# DSJA P4 AI Recruit

Canonical development base for the DSJA P4 Linkareer × NCS research system.

The primary scope is fixed to Linkareer recruitment postings from 2020-01
through 2026-07, AI·IT cohort selection, entry/intern/experienced structure,
entry-barrier requirements, and NCS duty-level analysis.

This repository starts a new Git history. The legacy repositories remain
immutable evidence sources and are referenced by commit and SHA-256 in
`manifests/legacy_sources.lock.yaml`; their generated runs are not imported as
Git authority.

## Safety boundary

- Local migration and observed replay only until a separately signed approval.
- Network-capable collection commands fail closed without `--approval-file`.
- Linkareer, external ATS, browser, and credentialed API calls are zero for the
  bootstrap migration.
- `data/raw`, large Parquet/DuckDB files, executed notebooks, API caches,
  embeddings, and LLM outputs are local-only.
- Observed-development data is never production or article authority.

## Quick start

```bash
uv sync --all-groups
uv run p4 contract validate
uv run p4 data verify
uv run p4 replay observed
uv run p4 qa run
uv run pytest
```

Research and promotion boundaries are defined in `docs/SSOT.md` and
`docs/ANALYSIS_CONTRACT.md`.
