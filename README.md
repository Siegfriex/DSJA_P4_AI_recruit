# DSJA P4 AI Recruit

Pure, local-first implementation base for the DSJA P4 Linkareer × NCS research
system.

## Current state

`PURE_BOOTSTRAP`: the repository contains contracts, source modules, tests,
environment examples, and implementation specifications. It intentionally
contains zero source, observed, processed, NCS, mart, release, or article-result
data.

Code existence is not execution authority. Collection, NCS promotion, marts,
analysis, and article results remain blocked until their evidence gates pass.

## Start here

```bash
uv sync --all-groups --locked
set -a
source env/bootstrap.env.example
set +a
uv run p4 env check
uv run p4 contract validate
uv run p4 data verify
uv run p4 status
uv run pytest
```

Expected bootstrap status:

- configuration: `PASS`
- contract bridge: `PASS`
- data registry: `EMPTY_BOOTSTRAP`
- repository status: `PURE_BOOTSTRAP_READY`
- source, collection, NCS, and analysis gates: `BLOCKED`

## Documentation authority

1. `docs/SSOT.md`
2. `docs/01_SYSTEM_DESIGN_SPEC.md`
3. `docs/02_DETAILED_DESIGN.md`
4. `docs/03_IMPLEMENTATION_RUNBOOK.md`
5. `contracts/registry.yaml` and the selected contract
6. `manifests/data_registry.yaml`
7. current run artifacts and tests

Historical migration evidence is reference-only and cannot populate the active
data registry without a new, explicit import decision.

## Safety boundary

- No network execution in bootstrap or observed mode.
- Canary and production require an external, unexpired approval bound to the
  current source-policy and query-registry hashes.
- A configured path does not make data trusted; registration, checksum,
  provenance, structural QA, and semantic QA are separate gates.
- Raw data, Parquet, DuckDB, executed notebooks, API caches, embeddings, model
  outputs, approvals, and credentials remain local-only.
- Never infer production, empirical, or article readiness from fixtures or
  structural tests.
