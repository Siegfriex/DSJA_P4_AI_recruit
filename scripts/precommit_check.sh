#!/usr/bin/env bash
set -euo pipefail

uv run p4 docs sync
uv run p4 docs check
uv run ruff check .
uv run pytest -ra
git diff --exit-code -- docs/00_master/P4_CURRENT_STATE.md \
  docs/00_master/P4_IMPLEMENTATION_STATUS.yaml \
  docs/00_master/P4_TRACEABILITY_MATRIX.csv \
  docs/08_evidence/CURRENT_EVIDENCE_INDEX.yaml \
  docs/11_release/ARTIFACT_REGISTRY.csv \
  docs/11_release/CURRENT_HASH_MANIFEST.sha256
