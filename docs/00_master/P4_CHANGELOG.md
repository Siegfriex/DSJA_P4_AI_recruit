# P4 Changelog

이 파일은 commit별 영향 기록이다. 자동 추론할 수 없는 semantic 영향은 `REVIEW_REQUIRED`로 남긴다.

## 2026-08-09 · c1cdec4f56e1

- commitSha: `c1cdec4f56e174c9d15734afd3be7cffcfef1abe`
- changeClass: `DOCUMENTATION`
- affectedArtifactIds: `P4-DPDD-SSOT-1.0.0`
- code paths: `docs/**`
- contract impact: `baseline import`
- data impact: `none; no empirical bytes`
- analysis impact: `definitions only; analysis remains blocked`
- required rerun: `p4 docs check`
- gate impact: `DPDD_SSOT_V1_IMPORTED`
## 2026-08-09 · 464ec546c637

- commitSha: `464ec546c637bc92c1d107ad5ab1d6b2e4e3de17`
- changeClass: `REVIEW_REQUIRED`
- affectedArtifactIds: `config/gates.yaml, config/ncs_scope.yaml, config/periods.yaml, config/project.yaml, config/query_registry.yaml, config/run_modes.yaml, config/source_policy.yaml, contracts/registry.yaml, contracts/schemas/v4_extensions/api_endpoint_contract.schema.json, contracts/schemas/v4_extensions/api_probe_run.schema.json, contracts/schemas/v4_extensions/calibration_model.schema.json, contracts/schemas/v4_extensions/candidate_packet.schema.json, contracts/schemas/v4_extensions/ncs_duty_unit_bridge.schema.json, contracts/schemas/v4_extensions/ncs_edge.schema.json, contracts/schemas/v4_extensions/ncs_external_code_crosswalk.schema.json, contracts/schemas/v4_extensions/ncs_node.schema.json, contracts/schemas/v4_extensions/ocr_quality.schema.json, contracts/schemas/v4_extensions/reference_label.schema.json, contracts/schemas/v4_extensions/semantic_chunk.schema.json, contracts/schemas/v4_extensions/source_block.schema.json, contracts/v2.1.2_legacy/CHECKSUMS.sha256, contracts/v2.1.2_legacy/CONTRACT_MANIFEST.json, contracts/v2.1.2_legacy/data_dictionary.csv, contracts/v2.1.2_legacy/data_dictionary.xlsx, contracts/v2.1.2_legacy/erd.mmd, contracts/v2.1.2_legacy/metrics.yaml, contracts/v2.1.2_legacy/p4_contract.schema.json, contracts/v2.1.2_legacy/p4_contract.yaml, contracts/v2.1.2_legacy/warehouse_duckdb.sql, contracts/v2.1.3_bridge/CHECKSUMS.sha256, contracts/v2.1.3_bridge/bridge.schema.json, contracts/v2.1.3_bridge/p4_contract.yaml, contracts/v2.1.3_bridge/warehouse_duckdb.sql`
- code paths: `.env.example, .gitignore, .python-version, README.md, artifacts/.gitkeep, config/gates.yaml, config/ncs_scope.yaml, config/periods.yaml, config/project.yaml, config/query_registry.yaml, config/run_modes.yaml, config/source_policy.yaml, contracts/registry.yaml, contracts/schemas/v4_extensions/api_endpoint_contract.schema.json, contracts/schemas/v4_extensions/api_probe_run.schema.json, contracts/schemas/v4_extensions/calibration_model.schema.json, contracts/schemas/v4_extensions/candidate_packet.schema.json, contracts/schemas/v4_extensions/ncs_duty_unit_bridge.schema.json, contracts/schemas/v4_extensions/ncs_edge.schema.json, contracts/schemas/v4_extensions/ncs_external_code_crosswalk.schema.json, contracts/schemas/v4_extensions/ncs_node.schema.json, contracts/schemas/v4_extensions/ocr_quality.schema.json, contracts/schemas/v4_extensions/reference_label.schema.json, contracts/schemas/v4_extensions/semantic_chunk.schema.json, contracts/schemas/v4_extensions/source_block.schema.json, contracts/v2.1.2_legacy/CHECKSUMS.sha256, contracts/v2.1.2_legacy/CONTRACT_MANIFEST.json, contracts/v2.1.2_legacy/data_dictionary.csv, contracts/v2.1.2_legacy/data_dictionary.xlsx, contracts/v2.1.2_legacy/erd.mmd, contracts/v2.1.2_legacy/metrics.yaml, contracts/v2.1.2_legacy/p4_contract.schema.json, contracts/v2.1.2_legacy/p4_contract.yaml, contracts/v2.1.2_legacy/warehouse_duckdb.sql, contracts/v2.1.3_bridge/CHECKSUMS.sha256, contracts/v2.1.3_bridge/bridge.schema.json, contracts/v2.1.3_bridge/p4_contract.yaml, contracts/v2.1.3_bridge/warehouse_duckdb.sql, data/fixtures/README.md, env/README.md, env/fixture.env.example, env/observed-replay.env.example, manifests/data_registry.yaml, notebooks/README.md, pyproject.toml, scripts/check_source_notebooks.py, scripts/replay_raw29.py, scripts/secret_scan.py, src/p4/__init__.py, src/p4/analysis/__init__.py, src/p4/collection/__init__.py, src/p4/collection/approval.py, src/p4/collection/assets.py, src/p4/collection/canary.py, src/p4/collection/detail.py, src/p4/collection/index.py, src/p4/collection/policy.py, src/p4/collection/recorder.py, src/p4/collection/runner.py, src/p4/config.py, src/p4/io/__init__.py, src/p4/io/hashing.py, src/p4/io/paths.py, src/p4/marts/__init__.py, src/p4/marts/posting.py, src/p4/marts/results.py, src/p4/marts/timeseries.py, src/p4/ncs/__init__.py, src/p4/ncs/corpus.py, src/p4/ncs/reference.py, src/p4/ncs/retrieval.py, src/p4/ncs/source.py, src/p4/processing/__init__.py, src/p4/processing/dedup.py, src/p4/processing/eligibility.py, src/p4/processing/labels.py, src/p4/processing/producers.py, src/p4/processing/requirements.py, src/p4/processing/tracks.py, src/p4/qa/__init__.py, src/p4/qa/bundle.py, src/p4/qa/lineage.py, src/p4/qa/schema.py, tests/collection/test_approval.py, tests/collection/test_policy.py, tests/collection/test_recorder.py, tests/fixtures/activity_text.json, tests/fixtures/asset_metadata.json, tests/fixtures/detail_page.html, tests/fixtures/index_response.json, tests/fixtures/ncs_units_small.csv, tests/integration/test_contract.py, tests/integration/test_synthetic_raw_semantic_e2e.py, tests/marts/test_marts.py, tests/ncs/test_ncs.py, tests/processing/test_eligibility.py, tests/processing/test_requirements.py, tests/processing/test_tracks_dedup.py, tests/test_config.py, uv.lock`
- contract impact: `REVIEW_REQUIRED`
- data impact: `REVIEW_REQUIRED`
- analysis impact: `REVIEW_REQUIRED`
- required rerun: `uv run p4 docs sync && uv run p4 docs check`
- gate impact: `REVIEW_REQUIRED`
## 2026-08-09 · b31dd51c9c35

- commitSha: `b31dd51c9c35baa749433ea304e532a272f64415`
- changeClass: `REVIEW_REQUIRED`
- affectedArtifactIds: `docs/00_master/P4_CHANGELOG.md, docs/00_master/P4_CURRENT_STATE.md, docs/00_master/P4_IMPLEMENTATION_STATUS.yaml, docs/00_master/P4_TRACEABILITY_MATRIX.csv, docs/08_evidence/CURRENT_EVIDENCE_INDEX.yaml, docs/08_evidence/processing/P4_RAW29_CLEANROOM_20260809_001_ATTESTATION.yaml, docs/08_evidence/repository/PRE_CLEANROOM_ARCHIVE_ATTESTATION.yaml, docs/09_governance/CLEANUP_LEDGER.csv, docs/11_release/ARTIFACT_REGISTRY.csv, docs/11_release/CURRENT_HASH_MANIFEST.sha256, docs/11_release/DOCUMENT_IMPORT_ATTESTATION.yaml, docs/11_release/source_v1.0.0/ARTIFACT_REGISTRY_v1.0.0.csv, docs/11_release/source_v1.0.0/EVIDENCE_MANIFEST_v1.0.0.sha256, docs/11_release/source_v1.0.0/P4_RELEASE_MANIFEST_v1.0.0.yaml, docs/11_release/source_v1.0.0/P4_TRACEABILITY_MATRIX_v1.0.0.csv`
- code paths: `.github/workflows/ci.yml, docs/00_master/P4_CHANGELOG.md, docs/00_master/P4_CURRENT_STATE.md, docs/00_master/P4_IMPLEMENTATION_STATUS.yaml, docs/00_master/P4_TRACEABILITY_MATRIX.csv, docs/08_evidence/CURRENT_EVIDENCE_INDEX.yaml, docs/08_evidence/processing/P4_RAW29_CLEANROOM_20260809_001_ATTESTATION.yaml, docs/08_evidence/repository/PRE_CLEANROOM_ARCHIVE_ATTESTATION.yaml, docs/09_governance/CLEANUP_LEDGER.csv, docs/11_release/ARTIFACT_REGISTRY.csv, docs/11_release/CURRENT_HASH_MANIFEST.sha256, docs/11_release/DOCUMENT_IMPORT_ATTESTATION.yaml, docs/11_release/source_v1.0.0/ARTIFACT_REGISTRY_v1.0.0.csv, docs/11_release/source_v1.0.0/EVIDENCE_MANIFEST_v1.0.0.sha256, docs/11_release/source_v1.0.0/P4_RELEASE_MANIFEST_v1.0.0.yaml, docs/11_release/source_v1.0.0/P4_TRACEABILITY_MATRIX_v1.0.0.csv, scripts/build_cleanup_ledger.py, scripts/precommit_check.sh, scripts/update_changelog.py, src/p4/cli.py, src/p4/docs/__init__.py, src/p4/docs/changelog.py, src/p4/docs/hashing.py, src/p4/docs/registry.py, src/p4/docs/release.py, src/p4/docs/status.py, src/p4/docs/sync.py, src/p4/docs/traceability.py, src/p4/docs/validate.py, src/p4/governance/__init__.py, src/p4/governance/attestation.py, tests/governance/test_attestation.py`
- contract impact: `REVIEW_REQUIRED`
- data impact: `REVIEW_REQUIRED`
- analysis impact: `REVIEW_REQUIRED`
- required rerun: `uv run p4 docs sync && uv run p4 docs check`
- gate impact: `REVIEW_REQUIRED`
## 2026-08-09 · a2bc6716c7fc

- commitSha: `a2bc6716c7fcc9b4da07ab04d7022fea59814280`
- changeClass: `REVIEW_REQUIRED`
- affectedArtifactIds: `docs/00_master/P4_CHANGELOG.md`
- code paths: `docs/00_master/P4_CHANGELOG.md, src/p4/docs/sync.py`
- contract impact: `REVIEW_REQUIRED`
- data impact: `REVIEW_REQUIRED`
- analysis impact: `REVIEW_REQUIRED`
- required rerun: `uv run p4 docs sync && uv run p4 docs check`
- gate impact: `REVIEW_REQUIRED`
## 2026-08-09 · 5a5dd5fd7c20

- commitSha: `5a5dd5fd7c201ae2b0c0092a57971df1e3ed04b2`
- changeClass: `REVIEW_REQUIRED`
- affectedArtifactIds: `REVIEW_REQUIRED`
- code paths: `src/p4/docs/sync.py`
- contract impact: `REVIEW_REQUIRED`
- data impact: `REVIEW_REQUIRED`
- analysis impact: `REVIEW_REQUIRED`
- required rerun: `uv run p4 docs sync && uv run p4 docs check`
- gate impact: `REVIEW_REQUIRED`
## 2026-08-09 · 4cc1207ac595

- commitSha: `4cc1207ac5953976176c73e15c9f04bd085b3877`
- changeClass: `REVIEW_REQUIRED`
- affectedArtifactIds: `REVIEW_REQUIRED`
- code paths: `.github/workflows/ci.yml, src/p4/docs/status.py`
- contract impact: `REVIEW_REQUIRED`
- data impact: `REVIEW_REQUIRED`
- analysis impact: `REVIEW_REQUIRED`
- required rerun: `uv run p4 docs sync && uv run p4 docs check`
- gate impact: `REVIEW_REQUIRED`
## 2026-08-09 · 8fe242ac72ed

- commitSha: `8fe242ac72ed984267f6cae46ec398375c96231a`
- changeClass: `REVIEW_REQUIRED`
- affectedArtifactIds: `REVIEW_REQUIRED`
- code paths: `.github/workflows/ci.yml, src/p4/docs/status.py`
- contract impact: `REVIEW_REQUIRED`
- data impact: `REVIEW_REQUIRED`
- analysis impact: `REVIEW_REQUIRED`
- required rerun: `uv run p4 docs sync && uv run p4 docs check`
- gate impact: `REVIEW_REQUIRED`
